from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from guard_eval.models import EvaluationRun, RunStatus, to_jsonable


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="guard_eval", description="Evaluate vietnamizer edit guards")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate an evaluation corpus")
    validate.add_argument("--manifest", required=True)

    evaluate = subparsers.add_parser("evaluate", help="evaluate a corpus split")
    evaluate.add_argument("--manifest", required=True)
    evaluate.add_argument("--config", required=True)
    evaluate.add_argument("--split", choices=("dev", "holdout"), required=True)
    evaluate.add_argument("--output", required=True)

    fit = subparsers.add_parser("fit-policy", help="fit a policy from a complete dev run")
    for name in ("manifest", "config", "run", "output"):
        fit.add_argument(f"--{name}", required=True)

    report = subparsers.add_parser("report", help="report metrics for a frozen policy")
    for name in ("manifest", "config", "policy", "pricing", "run", "output"):
        report.add_argument(f"--{name}", required=True)

    all_command = subparsers.add_parser("all", help="validate, evaluate holdout, and report")
    for name in ("manifest", "config", "policy", "pricing", "split", "output-dir"):
        all_command.add_argument(f"--{name}", required=True)
    return parser


def _make_adapter(config):
    from guard_eval.typesafe_adapter import TypeSafeAdapter

    return TypeSafeAdapter(config)


def _write_json(path: str, value) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(to_jsonable(value), ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _read_run(path: str) -> EvaluationRun:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("run root must be an object")
        return EvaluationRun.from_dict(raw)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid run: {type(exc).__name__}") from exc


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate":
        from guard_eval.corpus import CorpusError, validate_manifest

        try:
            corpus = validate_manifest(args.manifest)
        except CorpusError as exc:
            print(f"invalid corpus: {exc}", file=sys.stderr)
            return 1
        print(f"valid corpus {corpus.corpus_version}: {len(corpus.dev) + len(corpus.holdout)} cases")
        return 0
    if args.command == "evaluate":
        if args.split != "dev":
            print("invalid evaluation: public evaluate accepts only --split dev", file=sys.stderr)
            return 1
        from guard_eval.config import ConfigError, load_evaluation_config
        from guard_eval.corpus import CorpusError, validate_manifest
        from guard_eval.evaluator import evaluate_cases

        try:
            corpus = validate_manifest(args.manifest)
            config = load_evaluation_config(args.config)
            run = evaluate_cases(corpus.dev, _make_adapter(config), split="dev", corpus_version=corpus.corpus_version, config=config)
            _write_json(args.output, run)
        except (CorpusError, ConfigError, OSError) as exc:
            print(f"invalid evaluation: {exc}", file=sys.stderr)
            return 1
        if run.run_status is RunStatus.INVALID:
            print("invalid evaluation: run integrity checks failed", file=sys.stderr)
            return 1
        if run.run_status is RunStatus.INCOMPLETE:
            print(f"incomplete evaluation: {run.counts['unchecked']} unchecked case(s)", file=sys.stderr)
            return 2
        print(f"complete evaluation: {run.counts['checked']} checked case(s)")
        return 0
    if args.command == "fit-policy":
        from guard_eval.config import ConfigError, load_evaluation_config
        from guard_eval.corpus import CorpusError, validate_manifest
        from guard_eval.policy import PolicyError, fit_policy

        try:
            corpus = validate_manifest(args.manifest)
            config = load_evaluation_config(args.config)
            run = _read_run(args.run)
            if run.corpus_version != corpus.corpus_version or run.config_version != config.config_version:
                raise PolicyError("run versions do not match manifest/config")
            policy = fit_policy(corpus.dev, run)
            _write_json(args.output, policy)
        except (CorpusError, ConfigError, PolicyError, ValueError, OSError) as exc:
            print(f"invalid policy fit: {exc}", file=sys.stderr)
            return 1
        print(f"candidate policy written: {policy.policy_version}")
        return 0
    if args.command == "report":
        from guard_eval.config import ConfigError, load_evaluation_config, load_pricing_snapshot
        from guard_eval.corpus import CorpusError, validate_manifest
        from guard_eval.policy import PolicyError, load_policy
        from guard_eval.report import ReportError, generate_report

        try:
            corpus = validate_manifest(args.manifest)
            config = load_evaluation_config(args.config)
            policy = load_policy(args.policy)
            pricing = load_pricing_snapshot(args.pricing, expected_model=config.model_version)
            run = _read_run(args.run)
            report = generate_report(corpus.holdout, run, policy, pricing)
            _write_json(args.output, report)
        except (CorpusError, ConfigError, PolicyError, ReportError, ValueError, OSError) as exc:
            print(f"invalid report: {exc}", file=sys.stderr)
            return 1
        if report["run_status"] == RunStatus.INVALID.value:
            print("invalid report: integrity checks failed", file=sys.stderr)
            return 1
        if report["run_status"] == RunStatus.INCOMPLETE.value:
            print("incomplete report: unchecked holdout cases", file=sys.stderr)
            return 2
        print(f"complete report: decision={report['decision']}")
        return 0
    if args.command == "all":
        if args.split != "holdout":
            print("invalid all run: --split must be holdout", file=sys.stderr)
            return 1
        from guard_eval.config import ConfigError, load_evaluation_config, load_pricing_snapshot
        from guard_eval.corpus import CorpusError, validate_manifest
        from guard_eval.evaluator import evaluate_cases
        from guard_eval.policy import PolicyError, load_policy
        from guard_eval.report import generate_report

        try:
            corpus = validate_manifest(args.manifest)
            config = load_evaluation_config(args.config)
            policy = load_policy(args.policy)
            pricing = load_pricing_snapshot(args.pricing, expected_model=config.model_version)
            run = evaluate_cases(corpus.holdout, _make_adapter(config), split="holdout", corpus_version=corpus.corpus_version, config=config)
            output_dir = Path(args.output_dir)
            _write_json(str(output_dir / "holdout-run.json"), run)
            report = generate_report(corpus.holdout, run, policy, pricing)
            _write_json(str(output_dir / "holdout-report.json"), report)
        except (CorpusError, ConfigError, PolicyError, ValueError, OSError) as exc:
            print(f"invalid all run: {exc}", file=sys.stderr)
            return 1
        if report["run_status"] == RunStatus.INVALID.value:
            print("invalid all run: integrity checks failed", file=sys.stderr)
            return 1
        if report["run_status"] == RunStatus.INCOMPLETE.value:
            print("incomplete all run: unchecked holdout cases", file=sys.stderr)
            return 2
        print(f"complete all run: decision={report['decision']}")
        return 0
    print(f"guard_eval {args.command}: not implemented", file=sys.stderr)
    return 1
