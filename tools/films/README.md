# Making film libraries

How the trade film libraries were made (plumbing 30 Oct 2026, the other nine trades 5 Nov 2026).

- `plan.py`: every library film with its prompts (after still, before edit, film). `python3 plan.py <group> after|before|video` prints them.
- `jobs_trades.json` / `jobs_plumbing.json`: the Higgsfield job IDs and result links for every still and film (`_v1` = a rejected first try).
- `sheet.py`: contact sheet of the stills (`python3 sheet.py <group> before after`).
- `qa12.py`: 12 frames from each film between 12% and 92%, 5 films a sheet. Look for hands, arms or people walking in, and odd morphs. 3 of 90 needed a redo (a hand with a brush, a hand with a roller, a ballooning ceiling).
- `colours.py`: picks each film's accent from the part of the picture the work changed (ignores the floor and sky), then the darker ink, the dark-mode ink and the page ground, all checked for contrast. `OVERRIDE` holds hand-picked source colours.

Steps for one film (about 7 credits):
1. After still: `gpt_image_2_5`, 9:16, quality high (1.5 credits).
2. Before still: the same model with the after still as `image_references` and "Edit this exact photo. Keep the identical camera position..." (1.5 credits). Check the pair side by side: if the before barely differs, say what must be gone ("no drawers and no cupboard under the stairs: ...").
3. Film: `seedance_2_0_mini`, start_image = before job, end_image = after job, 9:16, 4 s, 720p, `generate_audio` false, `declined_preset_id` 24bae836-2c4a-48e0-89b6-49fcc0b21612 (4 credits). The prompt ends "The scene stays empty of people; nobody walks in or reaches into the frame." Avoid verbs that need a person ("trowelled", "painted with a roller").
4. QA with `qa12.py`, then `python3 engine/film_frames.py film.mp4 engine/films/<group>/<id>` and add the film to `FILMS` in trades.py with its colours.
