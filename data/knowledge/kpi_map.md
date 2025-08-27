# kpi map — syris. / calm.

purpose
- map each artifact or deliverable to measurable KPIs.
- ensure haruka always outputs a `kpi_impact` note when generating client-facing work.
- link every claim to evidence (artifact path or dataset).

shared kpis
- content_assets_published_per_week
- qualified_leads_per_week
- site_to_call_conversion_rate
- briefs_ready

calm.ops kpis
- pipeline_opportunities_created
- proposals_sent
- signed_deals
- ops_playbooks_created
- hours_saved_estimated

calm.life kpis
- subscribers_growth
- program_enrollments
- completion_rate_foundation
- habit_adherence_score
- testimonials_collected

example mapping
artifact: outreach_examples.md
- kpis: qualified_leads_per_week, pipeline_opportunities_created
- evidence: saved artifact file, client responses

artifact: proposal_clientX_2025-08-26.md
- kpis: proposals_sent, signed_deals
- evidence: proposal pdf, artifact path

artifact: calm.life_foundation_plan.md
- kpis: program_enrollments, completion_rate_foundation
- evidence: plan doc, user onboarding data

guardrails
- never output a proposal or outreach draft without mapping at least 1 KPI.
- every artifact must reference its file path or evidence.
- if unsure which kpi applies, pick the closest shared metric and flag with a note.

