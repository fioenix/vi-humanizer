# Motioneer · Gate 0 — Creative Direction Test: Vietnamizer

Date: 03/10/2026 · Subject: `fioenix/vietnamizer` at branch `codex/public-oss-cleanup` (0.9.7, unreleased, uncommitted changes in tree)

---

## Phase 1 — What the repository actually shows

**Sources read:** `SKILL.md` (whole), `README.md` (whole), both `profiles/*/rules.md` (B and K patterns), `profiles/blog-ca-nhan/styles/marketing-thuyet-phuc.md`, `references/bo-giai-phong-cach.md`, `calibration/LOG.md`, `calibration/ca-kiem-thu.md`, `scripts/scan-tells.sh`, `assets/*.svg`, `agents/openai.yaml`, `specs/README.md`, `eval/guard/README.md`, both guard-eval holdout reports, `docs/typesafe-removal-2026-10-03.md`, git history, working-tree status.

### 1. What it demonstrably is (the artifact itself)

- A **Markdown-only agent skill**. There is no runtime code and no build step. The "engine" is an editorial rulebook that an agent (Claude, Codex, anything Skills CLI supports) follows.
- The pipeline written in `SKILL.md`:
  1. **Genre gate.** Legal text, contracts, official letters, ritual and ceremonial prose, classical translation, poetry, changelogs, commit messages, error strings and UI labels get **typography only (T1–T6)**.
  2. **Preserved zones.** Code, schemas, structured data, parameter tables, verbatim quotes, proper names and examples under discussion are **frozen byte for byte**, then restored and byte-compared after editing.
  3. **One base profile and at most one style card per section.** There are 2 profiles and 7 cards, picked from five context dimensions: purpose, reader and relationship, register, channel and voice evidence.
  4. **55 named patterns:** V1–V25 for word use and sentence structure, T1–T6 for typography, B1–B17 for blog/personal/marketing and K1–K7 for technical/enterprise/academic. Every pattern has four parts: **Signal / Why / Fix / Do-not-flag**.
  5. **Five gate rules for every single edit:** the error must have a name; no new facts; meaning, certainty and register stay the same; the edit stays inside the smallest scope; no process metadata.
  6. **Re-read** the edited sentences. Never swap words just for variety.
- **Distribution plumbing:** a Claude Code plugin, a Codex plugin catalog, Skills CLI, a Claude Desktop `.skill` file and a Claude Org ZIP, plus a validator and packaging scripts. The 0.9.7 notes describe the tests as passing.

### 2. What the documentation claims (the claims hold, but only an LLM following the rules realises them)

- That it edits like a native Vietnamese editor and keeps the author's voice. Evidence for this is qualitative: **gold rewrites by a native speaker** recorded in `calibration/LOG.md`, plus **manual** test cases (the repo says plainly that there is no automated runner).
- 0.9.0 added V23–V25 and K7 after calibrating on **24 Vietnamese cases (12 positive, 12 anti-overcorrection)**.

### 3. Experimental, optional or retired

- **TypeSafe/Jev**: optional, and only used when the host already provides the official skill and the user consents to sending text. All TypeSafe code (advisor CLI, guard_eval v1/v2, SDK dependency) was **removed** in 0.9.7.
- **Guard-eval experiments (specs 001/002)**: kept as history only. Their outcomes were *stop* ("a required recall/accuracy metric decreased") and *collect_more_labels* ("insufficient denominator"). They prove **nothing** about efficacy.
- **Memory-based voice profiles**: removed in 0.9.7. The skill now uses only a sample or profile the user supplies inside the task.
- `scan-tells.sh`: a regex pre-scan that a maintainer runs. It is not part of the product's judgment.

### 4. What separates it from a generic "AI humanizer"

- **It is written in Vietnamese from the ground up, not translated.** Several rules *invert* the English humanizer playbook:
  - the en dash `–` is valid Vietnamese (*Hà Nội – Lào Cai*);
  - curly quotes are fine, and only mixing styles is a problem;
  - repeating a noun is correct cohesion, while synonym-cycling is the error.
- **Restraint is designed in.** Every one of the 55 patterns ships with an explicit *do-not-flag* list. The skill states that a pattern which deletes valid content does more harm than one that misses an error.
- **Register-aware in both directions.** It stops a report from being dragged into chat tone, and it gives jargon *back* when the real community uses it ("đội kỹ thuật" → "team dev", from the first gold rewrite).
- **The problems are Vietnamese-only:**
  - missing result complements (*giải quyết* → *giải quyết **được***);
  - two-syllable words cut to one (*hụt* → *hụt hẫng*);
  - classifiers (*ba **con** mèo*);
  - sentence-final particles (*nhé, nhỉ, ạ*);
  - pronouns tied to age and rank, which it **refuses to guess**;
  - home-made four-syllable Sino-Vietnamese slogans, while it leaves real policy terms alone (*phát triển bền vững*).
- **Calibration is public and honest about its own wounds.** The log records that the skill's own T4 fix created a new tell (*mà* outnumbering *nhưng* about 6:1) and how that was undone.
- **It is explicitly not an AI detector** and never infers authorship from errors.

---

## Phase 2 — Product Truth

**What it fundamentally is.** An editorial conscience for AI agents that write Vietnamese: a rulebook that makes the agent fix only the errors it can name, in the smallest possible scope, without changing facts, certainty or the writer's voice.

**The problem.** AI-drafted and translated Vietnamese is often grammatical but *hụt*. It drops small words, keeps an English skeleton (redundant *của*, plural *các*, *được… bởi*, em dashes, Title Case), slips into slogan rhythm and uses flat pronouns. Generic humanizers either don't know Vietnamese or overcorrect: they flatten register, strip jargon, invent details and "fix" correct text.

**Who it is for** *(inference: the repo defines genres, not personas).* Vietnamese-language writers who work through Claude Code, Codex or Claude apps. That covers developers writing READMEs, operations and product people writing SOPs and reports, and creators and marketers writing LinkedIn, Threads or blog content from AI drafts.

**What makes it different.** It reads the genre first, freezes what must not change, and treats *not editing* as a first-class outcome.

**What it explicitly is not:**
- an AI detector or detector-evasion tool;
- a paraphraser or "rewrite in any tone" converter;
- a translator;
- a spelling-standard enforcer (*hoà/hòa*, *kỹ/kĩ*);
- a memory or voice-cloning system;
- a SaaS or API;
- a product that depends on TypeSafe.

### Strongest defensible truths

1. **It adds the missing small piece instead of rewriting the sentence.** Scope minimality is a hard rule, and the calibrated examples are one-word insertions.
2. **All 55 patterns carry an explicit list of what not to touch.**
3. **Genre decides what may be edited:** law, poetry, ritual and changelogs get punctuation only, and code, quotes and names stay byte-identical.
4. **Voice and register survive the edit:** regional speech (*mắc quá, chi rứa*), real jargon, the author's pronouns and the stated level of certainty.
5. **It is built for Vietnamese specifically and calibrated against native-speaker rewrites in a public log,** including its own mistakes.

### Claims that must not appear in marketing

- "Undetectable", "bypasses AI detectors" or anything about evading detection. The product rejects that framing.
- Any percentage or quality-uplift number. No corpus supports thresholds, and the guard experiments ended in *stop* and *collect more labels*.
- "Verified by TypeSafe/Jev" or "AI-validated edits". That is optional, host-dependent and now code-free.
- "Learns your voice" or "remembers how you write". That was removed in 0.9.7.
- "Official" or "featured" in the Anthropic or OpenAI directories. It is only a repo marketplace catalog.
- "Released", "v1" or "available now" before 0.9.7 is actually merged and released. The branch currently holds uncommitted changes.
- "Grammar checker for all Vietnamese" or "fixes everything". The scope is 55 named patterns.
- "Automated test suite for language quality". The language cases are manual.
- Any before/after on screen that did not come from a real run of the skill. Use the calibrated pairs, or record new runs.

---

## Phase 3 — Three competing concepts

The three concepts answer one question with three different verbs:
- **Concept 1** *adds* the smallest thing;
- **Concept 2** *refuses* to touch;
- **Concept 3** *transforms everything except the truth*.

---

### Concept 1 — **Dấu Trăng** (The Breve)

**Big Idea.** Vietnamese meaning lives in the smallest marks: one curve turns *a* into *ă*. Vietnamizer is the curve, a tiny thing that finds exactly where meaning leaks and supplies only that.

**Hero Motif: the breve ˘ from the product's own icon.** It is one stroke, violet `#9750C4` on light and mint `#7FE2CE` on dark, exactly as in `assets/icon.svg`. It behaves like a small, curious creature, close to a spirit-level bubble that senses when a line isn't level. It **shapeshifts through Vietnamese's stacked diacritics**: the curve opens into a tilde (˜), folds into a circumflex (ˆ), hooks into the horn of ơ/ư, and flattens into a comma. These are moves only Vietnamese script allows, because one letter can carry two marks (ẫ, ặ, ở).

**Narrative Arc**
- **Beginning.** Darkness. A clean sentence types itself: *"Đã thử ba cách mà vẫn không giải quyết vấn đề."* It is grammatical, but the baseline after *giải quyết* **sags** by a few pixels, like a beam missing a bolt. The breve drifts in, rolls along the baseline, finds the sag and unfurls into **được**. The line levels with a soft click.
- **Development.** The repairs become subtler and more Vietnamese:
  - *"hụt"* sits alone and the breve stretches into its missing half, the tilde of *hẫng*;
  - *"ba mèo"* gets **con**;
  - an em dash `—` is gently squeezed down into a comma;
  - a row of Title-Case Words is nudged down one cap at a time.
- **Climax.** One continuous take over a whole AI-drafted LinkedIn post. The breve flies through it like a hummingbird, stops at only a handful of places, and ignores everything else, including a poem quoted at the end, where it settles and simply rests.
- **Ending.** The breve rises above a lone *a* and lands: **ă**. The wordmark resolves with the approved tagline *"Giúp AI viết tiếng Việt giống con người hơn."*

**Visual Language**
- **Composition:** type is the set. Huge single lines on an empty field, macro-close on diacritics, then a slow pull-out to paragraph scale for the climax.
- **Typography:** a Vietnamese-first face whose stacked diacritics hold up at display size (Be Vietnam Pro is the obvious candidate). Code appears only as a frozen mono pane.
- **Motion personality:** curious, light and precise. The breve has weight and a little overshoot, and it never moves at full speed in a straight line.
- **Depth:** mostly 2.5D. Text lives on one plane, and the breve floats a few millimetres above it with a soft shadow, so it reads as a separate being.
- **Code-native graphics:** SVG path morphing between diacritic outlines, and variable-font interpolation for the sag and level. Every element can be drawn as vectors.
- **Transitions:** the breve *is* the transition. It carries the eye from sentence to sentence.
- **Colour logic:** a near-monochrome page, with the brand colour reserved **only** for the breve and the characters it supplies. Colour therefore means "Vietnamizer touched this".
- **Product information as visuals:** each repair is one named pattern, shown for half a beat as a tiny tag (*V1*, *V20*, *V5*, *T2*, *T1*). The climax's restraint is the "five gate rules" made visible: most of the paragraph stays grey and untouched.

**Signature Moments**
1. The baseline sags under a missing *được*, then snaps level when the breve fills it.
2. The breve morphs ˘ → ˜ and completes *hụt → hụt hẫng*, one stroke turning into another letter's mark.
3. The breve lands on a line of lục bát poetry, folds itself up like a bird and does nothing. The poem stays grey.
4. The final *a → ă* landing, the only moment the breve stops being a creature and becomes a letter.

**Audio Strategy: sound-designed, no narration.** A sparse, warm palette of felt piano and plucked đàn bầu harmonics used *as texture*, not as a "Vietnam" cliché. Each correct repair resolves a tiny dissonance into consonance, so the sag is a slightly flat note and the fix tunes it. Diacritic morphs get soft paper and ink foley. Silence over the poem.

**Distribution.** Primary: a 16:9 hero film for the GitHub README, landing page and YouTube, **45–60 s**. Legato pacing, with long takes and few cuts. Derivative: a 4–5 s seamless loop of the *a → ă* landing for the README header and social avatar.

**Why this belongs to Vietnamizer.** The motif is literally the product's logo. Its behaviour, completing meaning with the smallest stacked mark, only exists in Vietnamese script and maps one-to-one onto real patterns (V1, V20, V5, T1, T2) and onto rule 4 (smallest scope). Swap in another developer tool and the breve has nothing to complete.

**Risks**
- **Diacritic cliché:** "Vietnamese brand = floating accent marks" can read as tourism graphics. The breve must act on real errors, not decorate.
- **Too cute:** a character with eyes or a face would kill it. It has to stay a stroke.
- **It mostly shows *adding*,** while the product's sharpest edge is *not touching*. The poem beat carries that, but only lightly.
- **Readability:** the before/after must be legible within a second, or non-editors miss the fix entirely.

---

### Concept 2 — **Khựng** (The Flinch)

**Big Idea.** The most interesting thing about this editor is what it refuses to change. The film is a game of temptations: an eager editing stroke charges at text that looks wrong by English humanizer logic, and stops dead, a pixel short, every time it would have broken correct Vietnamese.

**Hero Motif: a single red strike-through line, the reflex to "fix".** It behaves like a spring under tension: anticipation, a lunge, then a freeze and a recoil. Over the film it changes from a thick, slashing red bar into a thin violet/mint hairline that, at the end, touches **exactly one syllable**. The line is learning restraint as we watch.

**Narrative Arc**

*Beginning.* A HUD appears: `LEVEL 1`. One sentence sits centre-screen: *"tuyến Hà Nội – Lào Cai"*. The red line locks onto the en dash, lunges and **freezes** 1 px short. A tiny caption appears: *"– là gạch ngang tiếng Việt."* The line retracts.

*Development.* The levels come faster, and each trap is a real *do-not-flag* case from the repo:

| Level | Trap | What the line wants to do | Why it stops |
|---|---|---|---|
| 2 | *"Mắc quá nghen"* | normalize regional speech | voice is preserved |
| 3 | *khách hàng… khách hàng… khách hàng* | vary synonyms | repetition is cohesion |
| 4 | *"team dev"* | translate it to "đội kỹ thuật" | the community says *team dev*; the line even *restores* it |
| 5 | *"phát triển bền vững"* | kill a four-syllable slogan | it's a policy term, which B12 calls its most dangerous false positive |
| 6 | *"Bạn"* | swap to *em/anh* | don't guess age or rank |
| 7 | a contract clause | rewrite | only punctuation may pass the gate |
| 8 | a code block | edit | frozen glass, byte-identical |

The HUD tracks a "temptation meter" that keeps spiking and never pays out.

*Climax.* `FINAL LEVEL`. *"Câu này đúng ngữ pháp nhưng đọc lên thấy hụt."* For the first time the line does not flinch. Thin and careful now, it slides in and writes one syllable: **hẫng**. The meter drains. Reward sound.

*Ending.* `55 pattern. 55 danh sách "Không flag".` Wordmark.

**Visual Language**
- **Composition:** one sentence per level, enormous, centred, on a flat field, like an arcade stage. The HUD sits at the edges, pixel-crisp and monospaced.
- **Typography:** a heavy grotesk for the traps, so the text feels like an obstacle, and mono for the HUD and the freeze captions.
- **Motion personality:** comic timing, built on anticipation, overshoot and the held freeze-frame. The animation lives in **near-misses**, not in things appearing.
- **Depth:** flat 2D on purpose. It is a game screen, and the drama is time, not space.
- **Code-native graphics:** the line is a spring-physics SVG stroke. Freeze frames use a chromatic hairline jitter, and the HUD is plain DOM/Canvas text.
- **Transitions:** hard cuts on the beat, plus `LEVEL n` slams.
- **Colour logic:** red means the English-rule reflex, violet/mint means Vietnamizer's precise mark, and grey means text correctly left alone. The red slowly desaturates into brand colour across the levels.
- **Product information as visuals:** each level *is* a rule (genre gate, preserved zone, V19, B12, B15, the no-synonym rule). "55 patterns, each with a do-not-flag list" stops being a bullet and becomes the scoring system of the game.

**Signature Moments**
1. The first freeze: a lunging red bar stops 1 px from *Hà Nội – Lào Cai*, holds three frames, and trembles.
2. The *team dev* level: the line flips direction and *un-translates* a word. The fix runs backwards.
3. The code level: the line hits a pane of glass, cracks the glass's reflection and leaves the code intact.
4. The final level: the line no longer flinches, and the screen goes quiet for one syllable.

**Audio Strategy: sound-designed and rhythmic, no voice.** A minimal, driving beat (8-bit-adjacent, not chiptune pastiche). Every lunge rises in pitch. Every flinch cuts *all* audio to dead silence for the freeze, then a soft rewind-tick on the recoil. The silence is the hook. On the final level the beat drops out and only one clean tone plays as *hẫng* is written.

**Distribution.** Primary: 9:16 vertical for Threads, LinkedIn mobile, TikTok and Reels, **30–40 s**. Staccato pacing at about 3 s per level, with a seamless loop from the end card back to `LEVEL 1`. On-screen Vietnamese is large enough to read with the sound off.

**Why this belongs to Vietnamizer.** Every trap is lifted straight from the product's *do-not-flag* sections, and most of them are cases where the English humanizer rule is *wrong for Vietnamese*. The film cannot be re-skinned for another tool, because no other tool ships 55 explicit lists of what not to touch, and none has these Vietnamese traps. Developers know this pain instantly: it is a **linter that knows when to shut up**.

**Risks**
- **Negative framing:** "a tool that doesn't do things" can read as passive. The final level must deliver a satisfying, real fix.
- **Competitor-bashing tone:** the red line must stay an abstract reflex, never a named or caricatured competitor.
- **Literacy barrier:** the jokes land only for Vietnamese readers (acceptable, since that is the audience), but captions must be instant.
- **Becoming a list:** eight levels can turn into a feature carousel. Cut to the five sharpest if timing slips.
- **Red strike-through** echoes grammar-checker UI. The physics and the freezes have to carry identity, not the colour.

---

### Concept 3 — **Bất Biến** (Invariant)

**Big Idea.** The same fact turns up in a chat, a blog post, a README, a report. Vietnamizer edits each document in its own voice, and the fact never moves. *Giọng đổi, sự thật đứng yên.*

**Hero Motif: a pinned fact, the glyph-block `320 ms`.** This is the real figure from the calibration cases MS05/MS06. It is a small, solid object with a pin through it, and it is **the only thing in the film that never moves, recolours or reflows**. A second, smaller object is tethered to it by a thread: the caveat *"chưa đại diện cho tải thật"*, which stands for the level of certainty. At the very end the pin turns out to be the stem of **ă** in the logo.

**Narrative Arc**
- **Beginning.** The camera is locked to the pin. Around it, a **chat** space assembles from bubbles: *"Rà lại giúp mình trước 15 giờ nhé"*. The particle *nhé* stays, and the pronoun stays.
- **Development.** The world **folds around the pin like paper**, and each fold reveals a different *existing* document carrying the same fact:
  - a first-person blog (*tôi* stays);
  - a README (*tôi* is absent because it never belonged there, and the code fence is frozen glass);
  - an SOP with numbered steps;
  - an academic page with footnotes.

  Each room shows one small, genre-correct edit.
- **Pressure.** The marketing room tries to inflate the fact. *"Nhanh gấp 2,5 lần!"* slams against the pin and bounces off. *"có thể"* tries to harden into *"sẽ"* and snaps back. A scissor goes for the caveat, and the thread pulls it back. These are rules 2 and 3 (no new facts; certainty unchanged) made physical.
- **Climax.** All the rooms spin around the pin like a zoetrope at increasing speed while the pin stays perfectly still: the stable centre of a chaotic world. Locked doors flash past (law, poetry, ritual) where only punctuation slips through the keyhole.
- **Ending.** The rooms fall away. The pin stands alone, the bowl and breve of *ă* assemble around it, and the logo appears.

**Visual Language**
- **Composition:** strict centre-locked framing. Everything orbits the pin.
- **Typography:** each room is built *from its genre's typographic conventions*: chat bubbles, Markdown `#` headings, numbered SOP steps, academic superscripts. The pin is always set in one invariant face and size.
- **Motion personality:** architectural and calm, then centrifugal. Smooth folds turn into a vortex.
- **Depth:** true 3D folding of 2D planes, with an orbiting camera around a fixed point. This is the one concept that needs WebGL/three.js, or very careful CSS 3D.
- **Code-native graphics:** paper-fold shaders, typographic rooms generated from real Markdown, physics bounces for the rejected inflations.
- **Transitions:** folds pivot on the pin as their axis.
- **Colour logic:** each room takes its own muted palette. The pin and its thread are the only constant colour (brand mint/violet).
- **Product information as visuals:** the style resolver becomes architecture (rooms = cards, a locked door = the genre gate). The five gate rules become physics (things bounce off the pin).

**Signature Moments**
1. The first fold: the entire chat room creases and turns over around a pin that doesn't even quiver.
2. *"Nhanh gấp 2,5 lần!"* hits the pin like a thrown object and shatters into letters.
3. A scissor cuts the caveat's thread, and the thread *re-ties itself*.
4. The zoetrope climax: seven rooms blur into a ring while `320 ms` stays razor-sharp.

**Audio Strategy: hybrid.** A calm Vietnamese narrator speaks four or five short lines at most. Each room has its own sonic signature (chat pings, keyboard, printer, lecture-hall reverb), and the music **modulates key with every room**. One sustained drone, the sonic invariant, never changes pitch through any of it. Attentive viewers will *hear* the concept.

**Distribution.** Primary: 16:9 for YouTube, the landing page and conference talks, **60–75 s**. Measured pacing with long holds. Secondary: a 1:1 cut for the LinkedIn feed. Developers and team leads are the audience; this is the "trust" film.

**Why this belongs to Vietnamizer.** It visualises the style resolver, the precedence order and the "no new facts / same certainty" gate rules, using the product's own calibration data (800 → 320 ms, and the caveat it refuses to drop). The register shifts are Vietnamese-specific (*nhé*, *tôi*, pronouns tied to relationship).

**Risks**
- **Biggest truth risk:** it can easily read as "convert one text into seven tones", which Vietnamizer **does not do**. Every room must be shown as a *different pre-existing document* that the skill edits, never one sentence being restyled.
- **Generic "tone changer" look:** rooms as templates can resemble Grammarly-style tone UI.
- **Complexity:** a 3D fold plus a zoetrope can bury the idea under spectacle.
- **The invariant is abstract,** and needs the narrator to land it, which weakens the film for sound-off viewing.

---

## Phase 4 — Comparison and recommendation

| | 1 · Dấu Trăng | 2 · Khựng | 3 · Bất Biến |
|---|---|---|---|
| Core verb | adds the smallest piece | refuses to touch | changes everything but the truth |
| Truth expressed | scope minimality, Vietnamese specificity | do-not-flag discipline, inverted English rules | register-awareness, no new facts, certainty |
| Visual identity | strongest brand link (the motif is the logo) | strongest behaviour (near-miss timing) | strongest spatial spectacle |
| Truth risk | low | low | **high** (tone-converter misread) |
| Sound-off performance | good | **excellent** | weak |
| Primary channel | README / landing | Threads, LinkedIn, Reels | YouTube / talks |

**Recommendation: Concept 2, Khựng.**

- **The most truthful.** The single most differentiating fact in the repository is not a pattern. It is the *do-not-flag* half of every pattern, together with the rules where Vietnamese contradicts the English humanizer canon. Khựng is built entirely from those cases, so nothing on screen is invented.
- **The strongest identity is behaviour, not style.** One primitive, a line with a spring-loaded urge, carries the whole film, which is exactly the brief's "simple primitive with brilliant behaviour". Its signature, the held freeze a pixel short of the target, owns a moment no other launch film does.
- **Why developers will remember it.** Every developer has suffered a linter full of false positives. *"A linter that knows when to shut up"* lands in a second, and it fits the audience on Fio's channels (Threads and LinkedIn, concrete and slightly irreverent).
- **Why templates can't reproduce it.** Generic AI-video templates animate things *appearing*. This film's drama lives in things *almost happening*: anticipation, overshoot, a silence cut on the frame. And every trap requires Vietnamese linguistic knowledge (*–* in place names, *team dev*, *phát triển bền vững*, *bạn* vs *em*) that a template cannot generate.

**Honest trade-off.** Concept 1 is the better-looking film and the stronger long-term brand asset, because its motif *is* the logo. If the goal were a README hero loop rather than a launch hook, Concept 1 would win. Concept 3 is the most ambitious, but also the most likely to misrepresent what the product does.

---

## Decision

**03/10/2026 — Fio chose Concept 1, Dấu Trăng (The Breve).** This overrides the Phase 4 recommendation (Concept 2).

Carry these into Gate 1:
- **Restraint is under-weighted.** Concept 1 mostly shows the skill *adding* things. Its main weakness is that the strongest product truth, *not touching* correct text, rests on the single poem beat. Gate 1 should decide whether one or two refusals become real beats: the breve bouncing off a code pane, and the breve hovering over *Hà Nội – Lào Cai* and leaving it alone.
- **Avoid the diacritic cliché.** Every move the breve makes must fix a real, named error, never decorate.
- **Demo honesty.** Every repair on screen (*được*, *hụt hẫng*, *con*, em dash, Title Case) and the climax paragraph must come from calibrated pairs or recorded runs of the skill.

## Revision 1 — the single-sentence edit (Fio, 03/10/2026)

**Fio's direction:** the film centres on one very stiff, AI-sounding sentence. The breve *kicks out* words that don't belong, *inserts* missing words and *moves* words around, until the sentence reads like a person wrote it. This replaces the "series of separate repairs" in the original arc.

### The sentence (checked against the skill's rules; work-blog genre, prose)

**Before:**
> Điều quan trọng cần lưu ý là các lỗi của hệ thống đã được phát hiện bởi đội kỹ thuật trong quá trình kiểm tra, và đội vẫn không tìm nguyên nhân.

**After:**
> Đội kỹ thuật đã phát hiện lỗi hệ thống khi kiểm tra, nhưng đội vẫn không tìm ra nguyên nhân.

### Every operation and its named pattern

| # | Operation | What happens | Pattern |
|---|---|---|---|
| 1 | Kick | *Điều quan trọng cần lưu ý là* leaves the sentence | V11, an opener that adds no information |
| 2 | Move | *đội kỹ thuật* jumps from the middle to the front of the sentence | V16, a passive copied from English |
| 3 | Kick | *được* and *bởi* fall away, freed by the move | V16 |
| 4 | Kick | *các* | V8, a plural marker added by reflex |
| 5 | Kick | *của*, so *lỗi của hệ thống* becomes *lỗi hệ thống* | V7, a redundant *của* |
| 6 | Swap | *trong quá trình* becomes *khi* | V9, a long prepositional phrase copied from English |
| 7 | Swap | *, và* becomes *, nhưng*. The word *vẫn* already signals the contrast. | T4 |
| 8 | Insert | *ra*, so *không tìm* becomes *không tìm ra* | V1, a missing result complement |

**Kept on purpose:**
- *đã*, the only past-tense marker (V4 do-not-flag).
- The second *đội*. Repeating a noun is not an error, and dropping it would be a style choice no pattern backs.
- *khi kiểm tra* stays in its original position. It isn't ambiguous, so V10 does not allow moving it.

**Meaning check (rule 3):** the actor, the time, the level of certainty and the contrast are unchanged, and no new fact is added.

### Why the last insert is the climax

*không tìm nguyên nhân* literally means "did not look for the cause". *không tìm ra nguyên nhân* means "could not find the cause". A single syllable separates an accusation of negligence from an honest report. Every other operation removes weight; this is the only one that gives the sentence back its meaning. It also shows Vietnamese-specific grammar that no generic tool would touch.

### The breve's three moves

- **Kick:** the breve's curve becomes a scoop or catapult that flicks a word block off-frame with real physics, so the word tumbles, bounces and exits. The gap closes with a short spring.
- **Move:** the breve cups *đội kỹ thuật* like a spoon and lobs it in an arc to the front of the sentence. The words in between shuffle aside.
- **Insert:** the breve morphs into a hook or caret and sets the new word into the gap. The new word is the only text drawn in brand colour.

### Beat sheet for the core sequence (~25 s inside the 45–60 s film)

1. **0–4 s.** The stiff sentence types itself out in full, line-wrapped and heavy. Hold long enough for the viewer to feel the weight.
2. **4–7 s.** The breve enters and kicks out *Điều quan trọng cần lưu ý là*: the biggest object, the loudest kick.
3. **7–11 s.** The breve lobs *đội kỹ thuật* to the front. *được* and *bởi* lose their support and drop.
4. **11–15 s.** A quick triplet of small flicks: *các*, *của*, then *trong quá trình* swapped for *khi*. This is the rhythmic run.
5. **15–18 s.** *và* turns over and becomes *nhưng*.
6. **18–22 s.** Stillness. The breve hovers over the gap after *tìm*, sets down *ra*, and the baseline clicks level.
7. **22–25 s.** The finished sentence breathes. The kicked-out words lie scattered in a pile on the floor of the frame.

### Decisions after Revision 1

- **No pattern tags on screen** (Fio, 03/10/2026). The film stays text-only.
- **Demo:** `motioneer/demo/dau-trang.html`. HTML/SVG, 16:9 stage, about 30 s, no audio. Fio will request changes to the sentence if it is wrong.
- **Still open:** before filming, run this exact sentence through Vietnamizer 0.9.7 itself and record the output. This revision was checked against the rules of the installed `vi-humanizer` skill, which has the same V1–V25 and T1–T6 as the repo, but the film should show a real run of the product it advertises.

## Open items outside the creative choice

- **Shipping gate (resolved 03/10/2026).** Vietnamizer 0.9.7 was released as `v0.9.7` (GitHub release marked Latest), and the cleanup work was merged into `main` via PR #6. The install commands in the film can point at `main` and the release.
- **Demo honesty.** Every before/after on screen must come from the calibrated pairs or from recorded runs of the skill, never from invented text.
