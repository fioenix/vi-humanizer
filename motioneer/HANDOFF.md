# Motioneer — handoff

Launch-video work for Vietnamizer. This work lives only on branch `motioneer`; never merge it into `main` unless Fio says so.

## State (03/10/2026)

- **Gate 0 is done.** Fio chose **Concept 1, Dấu Trăng (The Breve)**, then narrowed it to a film about one sentence. Full reasoning, Product Truth, banned claims and decisions are in `gate-0-creative-direction.md` (read the Decision and Revision 1 sections first).
- **Demo:** `demo/dau-trang.html`. Self-contained HTML/SVG on a 16:9 stage, about 30 s, no audio. Open it in a browser and use the "Phát lại" button to replay.

## Locked decisions

- The breve from the logo (`assets/icon.svg`) is the only character. It has three moves: kick a word out, move a word, insert a word.
- **Before:** *Điều quan trọng cần lưu ý là các lỗi của hệ thống đã được phát hiện bởi đội kỹ thuật trong quá trình kiểm tra, và đội vẫn không tìm nguyên nhân.*
- **After:** *Đội kỹ thuật đã phát hiện lỗi hệ thống khi kiểm tra, nhưng đội vẫn không tìm ra nguyên nhân.*
- Every operation maps to a named pattern (V11, V16, V8, V7, V9, T4, V1). The insertion of *ra* is the climax.
- No pattern tags on screen.- Only the inserted words (*khi*, *nhưng*, *ra*) use the brand colour.

## Open

- The sentence pair was checked by hand against the rules. It is not yet the output of a real Vietnamizer run. Fio accepted this for the demo and will ask for fixes if the sentence is wrong.
- No audio yet; the concept calls for a sound-designed track.
- Dark mode is coded but has not been viewed.
