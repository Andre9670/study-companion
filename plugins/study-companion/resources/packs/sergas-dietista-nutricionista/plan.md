# Study plan — SERGAS Dietista-Nutricionista (concurso-oposición)

**Learner:** Andrea's friend. **Goal:** pass the oposición. **Mode:** hybrid (grounded on
provided láminas + open for the rest). **Set up:** 2026-09-09.

## Source policy (obey when filling gaps in open mode)
1. **Freshness:** prefer the most recent official version (2025–2026). Flag when a guide has a newer edition than the láminas.
2. **Geography/authority:** Galician (Xunta / SERGAS, e.g. Guías de Salud SERGAS) → Spanish (AESAN, Ministerio de Sanidad, sociedades científicas ES) → European (EFSA, ESPEN). **Exclude US clinical guidance** (e.g. ADA on diabetes) unless the learner asks.
3. **Primary over secondary:** the official convocatoria / temario / regulation beats summaries.
4. Source of truth for *scope*: the official convocatoria (DOG 19/12/2025, AnuncioG0003-111225-0001).

## Exam structure (Anexo III)
- **Ejercicio 1 (eliminatorio):** test 4 opciones — 50 teoría específica + 50 casos prácticos (150 min, 0–50, aprobado ≥25). Penalización: −25% del valor de acierto por error; en blanco = 0.
- **Ejercicio 2 (obligatorio, no eliminatorio):** 10 preguntas parte común (temas 1–8), 15 min, 0–5. Promoción interna exenta.
- **Ejercicio 3 (obligatorio, no eliminatorio):** 10 preguntas gallego, 15 min, 0–5. Celga 4 exento.
- **Fase de concurso:** hasta 40% del total (formación 20%/8pts, experiencia 70%/28pts, otras 10%/4pts).

## Temario
- **Parte común (8 temas):** Constitución/protección salud; Estatuto de Galicia; Ley general de sanidad; Ley de salud de Galicia/SERGAS; Estatuto marco; personal estatutario; protección de datos y consentimiento informado; PRL e igualdad/violencia de género.
- **Parte específica (46 temas — Anexo II):** bromatología, metabolismo de macronutrientes, valoración nutricional, dietoterapia (diabetes T28–29, cardiovascular, renal, respiratoria, neurológica, oncológica T34…), **TCA (temas 35–36, material en corpus)**, salud pública, epidemiología, seguridad alimentaria/APPCC, nutrición pediátrica/embarazo/geriatría, restauración colectiva, etc.
  - **Temario completo VERBATIM en `temario.md`** (8 común + 46 específica, Anexo II, DOG 245 19/12/2025). T35 = Psicología del comportamiento alimentario; T36 = Trastornos de la conducta alimentaria (ambos con material en corpus).

## Key dates
- DOG published 19/12/2025. **Inscripción: hasta 30/01/2026.** Tasa €38,02.
- Fechas de examen: por publicar en DOG (min. 5 días hábiles de antelación).

## Acceptance criteria (how we'll know studying is working)
- Every started topic reaches **mastery ≥ 0.8 at `apply` Bloom level**.
- No item overdue > 3 days (spaced-repetition kept current).
- Weak-area gap cheat sheet generated and reviewed at least once per topic block.
- Practice mirrors the real exam: 4-option MCQ + practical cases, with the −25% wrong-answer penalty modeled in scoring feedback.

## Status
- **Temario oficial completo** (8 común + 46 específica) capturado verbatim en `temario.md`.
- **Grounded:** temas 35–36 (psicología del comportamiento alimentario + TCA) ingeridos en `index.md`.
- **Sin banco de preguntas precargado (a propósito).** El tutor genera las preguntas cuando el/la estudiante quiere practicar.

## Cómo generar preguntas (instrucciones para el tutor)
El estado arranca vacío (`state/items.json`). Cuando el/la estudiante pida practicar un tema:
1. Elige el/los temas del `temario.md` (o el que indique el estudiante).
2. Genera ítems atómicos (una idea cada uno), variando el nivel Bloom (recall→understand→apply→analyze)
   e incluyendo **supuestos prácticos** (el examen tiene 50 preguntas de casos). Para T35/T36 usa
   **modo grounded** (solo desde `corpus/`+`index.md`, citando `Lámina N`); para el resto, **open mode**
   bajo la source policy (Galego/SERGAS 2025–26 → ES → EU; sin fuentes de EE. UU.).
3. Añádelos con el scheduler:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sm2.py add --state <ruta>/state/items.json --id <slug> --topic <tema> --bloom <nivel> --question "..." --answer "..." --keywords "k1,k2"`
4. Ejecuta el bucle de la skill `quiz` (confidence primero, sin dar la respuesta, pistas graduadas,
   explicación + keyword al fallar, `sm2.py grade`).
