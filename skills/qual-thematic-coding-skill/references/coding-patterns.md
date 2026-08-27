# Coding patterns for qual-thematic-coding-skill

## 1. Default output set

Use markdown as the default output layer:
- `01_individual_coding/P0X_thematic_coding.md`
- `02_cross_analysis/cross_interview_synthesis.md`
- `03_affinity_clustering/affinity_mapping_report.md`

Treat spreadsheet packaging as optional export, not the default requirement.

## 2. Five-category analysis lens

Review each transcript through these five lenses:
- key themes
- pain points
- workarounds
- emotional moments
- surprises

For key themes, aim for 3 to 5 major themes with supporting direct quotes.
Do not let every category force the same volume of output; let evidence density vary.

## 3. Team schema: Context, Content, Group

Use this structure consistently:
- Context: direct quote or grounded excerpt from the participant
- Content: researcher interpretation, meaning, or implication
- Group: higher-order theme label

If needed, allow multiple content notes under one quote, but keep the grounded quote visible.

## 4. Individual coding file pattern

Each participant file should usually contain:
- participant context summary
- key themes with supporting quotes
- pain points
- workarounds
- emotional moments
- surprises
- short analyst note on confidence or ambiguity

## 5. Cross-interview synthesis pattern

Use these synthesis buckets:
- consistent patterns
- contradictions
- spectrum findings
- outlier insights
- confidence assessment

Each synthesized point should include:
- analyst interpretation
- why it matters
- 1 to 3 directly relevant participant quotes or grounded excerpts

Do not leave the cross-interview section as paraphrase-only summary.
The reader should be able to see which user language supports each claim without opening every participant file.
Use verbatim quotes by default.
Do not insert `...`, rewrite wording into cleaner prose, or shorten the quote unless the original source is already truncated.
Format each quote so the reader can see source context without cross-opening files.
Default quote prefix pattern:
- `[문항 번호: {question_code} | 문항 출처: {protocol section or question topic} | PID: {P00X} | {age band} {gender} | {segment trait}] {verbatim quote}`

If one source label bundles several nearby probes, use the closest protocol question number that most directly elicited the quote.

Default confidence rule:
- High: repeated in 50% or more of relevant interviews with clear supporting evidence
- Medium: repeated enough to matter but limited by sample, segment split, or ambiguity
- Low: promising but sparse, contradictory, or dependent on weak evidence

Sort the synthesis by confidence first, then by strategic importance.

## 6. Affinity clustering rule

Cluster evidence naturally rather than forcing a preset taxonomy.
Aim for roughly 5 to 10 clusters unless the dataset is clearly much smaller.
For each cluster capture:
- cluster label
- representative quotes or observations
- why the cluster matters
- relationship to adjacent clusters if relevant

Also surface:
- outlier quotes that resist clustering
- possible causal or sequence links between clusters

## 7. Boundary with interview-quant-coding-skill

This skill is for open qualitative interpretation.
Use `$interview-quant-coding-skill` instead when the task needs:
- fixed tag lists
- true or false coding matrices
- frequency ranking tables
- composite scoring or segment scoring

## 8. Common failure modes

Watch for these mistakes:
- over-summarizing and losing quotes
- ignoring workarounds because they look like minor hacks
- flattening contradictions into fake consensus
- using mention count as the only importance signal
- turning affinity mapping into a rigid spreadsheet exercise too early
## 9. Companion workbook packaging rule

The default workbook should package the same evidence already preserved in markdown.
A practical sheet pattern is:
- `individual_coding_index`
- `cross_interview_synthesis`
- `affinity_clusters`
- optional participant-level or quote-level tabs when the dataset is large

Do not let the workbook replace the markdown evidence files.
Treat it as a synchronized companion artifact.
