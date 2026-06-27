#!/usr/bin/env python3
"""Validate Hoax.ai Non-Public Static Workbench Public-Readiness Boundary Governance v1."""
from __future__ import annotations
import json, re, subprocess, sys, xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
from public_surface_checks import (
    PUBLIC_SITEMAP_URL_COUNT,
    PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_PUBLIC_READINESS_BOUNDARY_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE,
    PUBLISHER_STATUS_GOVERNANCE_SCAFFOLDING_FREEZE,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PRODUCTION_BATCH_1,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PRODUCTION_BATCH_2,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PRODUCTION_BATCH_3,
    PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_STANDARD_V1,
    PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_PROTOCOL_V1_DRAFT,
    PUBLISHER_STATUS_POST_PUBLIC_INTERFACE_THESIS_EVIDENCE_FIELD,
    PUBLISHER_STATUS_POST_EVIDENCE_FIELD_STATIC_INTERFACE_EMBODIMENT_V1,
    PUBLISHER_STATUS_POST_EVIDENCE_FIELD_VISUAL_SYSTEM_ACCESSIBILITY_HARDENING,
    PUBLISHER_STATUS_POST_CONTROLLED_DOMAIN_CONNECTION_DECISION,
    PUBLISHER_STATUS_POST_ENGINE_BOUNDARY_AND_PUBLIC_REFERENCE_SEO_AUTHORITY_MAP,
    PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_ENGINE_MODEL_V0,
    PUBLISHER_STATUS_POST_OUTPUT_LANGUAGE_GUARDRAIL_MODEL_V1,
    PUBLISHER_STATUS_POST_INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_IMPLEMENTATION_SPRINT,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_VALIDATION,
    PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_TRACEABILITY_INTERPRETABILITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_VALIDATION,
    PUBLISHER_STATUS_POST_TARGETED_SYNTHETIC_FIXTURE_EXPANSION_V1_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_COMPOUND_BOUNDARY_STRESS_TEST_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_PACK_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_OUTPUT_ADMISSIBILITY_CONTRACT_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_ADMISSIBILITY_REGRESSION_SUITE_VALIDATION,
    PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_RELEASE_BLOCKER_BOARD_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_EXPOSURE_PREREQUISITE_MAP_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_COPY_BOUNDARY_FRAMEWORK_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_EVIDENCE_RISK_UTILITY_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_EXPANSION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_UTILITY_INTERFACE_EMBODIMENT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_AUTHORITY_INTERNAL_LINKING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SOURCE_CONFIDENCE_LAYER_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ANSWER_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_CITATION_RETRIEVAL_HARDENING_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_QUALITY_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_DEPTH_EXPANSION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PATHWAY_PAGES_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_IA_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SURFACE_AUTHORITY_REVIEW_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_ENTRY_POINTS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_NARRATIVE_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ACQUISITION_READINESS_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION,
    PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION,
    validate_public_surface,
)
PROTO_DIR=ROOT/'_internal_prototypes'/'evidence-posture-workbench'
LOCKED_FILES=['_internal_prototypes/evidence-posture-workbench/index.html','_internal_prototypes/evidence-posture-workbench/prototype.css']
MATURE='boundary_governance_only_no_public_release_no_engine_no_classifier_no_public_route'
POLICY='data/non-public-static-workbench-public-readiness-boundary-policy.json'
PROHIBITED=['prototype modification','new prototype files','prototype expansion','public route creation','sitemap expansion','public navigation link','public workbench','interface behavior','javascript','forms','inputs','upload','scoring','fake/real output','generated output','engine','classifier','detector','api','analytics','storage','network calls','monetization','dns','cloudflare','custom domain launch','deployment changes','external factual claims','subject accusation','python cache file commit']
BLOCKED=['public_release','public_route','sitemap_entry','public_navigation','public_workbench','public_engine','public_classifier','public_detector','upload','scoring','fake_real_output','generated_output','forms','inputs','API','analytics','monetization','DNS','Cloudflare','custom_domain_launch','deployment','prototype_modification','prototype_expansion','production_readiness']
PREREQS=['baseline_lock_validation_complete','public_readiness_boundary_governance_complete','public_readiness_boundary_validation_required','public_copy_boundary_governance_required','public_route_eligibility_governance_required','public_isolation_to_exposure_transition_governance_required','public_disclaimer_non_operation_language_governance_required','public_accessibility_validation_required','public_seo_canonical_indexability_decision_required','public_security_privacy_review_required','artifact_subject_separation_public_wording_audit_required','no_engine_classifier_upload_scoring_implication_audit_required','no_detector_pattern_regression_audit_required','deployment_gate_review_required','custom_domain_dns_gate_review_required_if_applicable']
RISKS=['prototype_mistaken_for_detector','not_assessable_mistaken_for_fake','output_envelope_mistaken_for_conclusion','artifact_posture_mistaken_for_subject_guilt','visual_prototype_mistaken_for_product','public_route_mistaken_for_launch','public_navigation_mistaken_for_tool_availability','search_snippet_misrepresentation','screenshot_context_loss','upload_scoring_expectation','public_use_for_real_world_accusations']
ROUTE_BLOCKERS=['public_readiness_boundary_validation_missing','public_route_eligibility_policy_missing','public_copy_boundary_missing','public_disclaimer_system_missing','public_indexing_policy_missing','public_navigation_policy_missing','public_risk_notice_missing','public_route_validator_missing','public_accessibility_audit_missing','public_seo_canonical_decision_missing','public_deployment_gate_missing']
SOURCE_LOCS=['NON_PUBLIC_STATIC_WORKBENCH_PUBLIC_READINESS_BOUNDARY_GOVERNANCE_V1.md','data/non-public-static-workbench-public-readiness-boundary-policy.json','data/non-public-static-workbench-public-readiness-non-authorization-rules-v1.json','data/non-public-static-workbench-public-readiness-required-prerequisites-v1.json','data/non-public-static-workbench-public-readiness-risk-boundary-v1.json','data/non-public-static-workbench-public-readiness-route-blockers-v1.json','data/non-public-static-workbench-public-readiness-boundary-audit-v1.json','validators/validate_non_public_static_workbench_public_readiness_boundary_governance.py']
NUMERIC=re.compile(r'\b(seo_score|quality_score|quality grade|score\s*[:=]|grade\s*[:=]|\d+\s*%)\b',re.I)
def error(m): print(f'ERROR: {m}')
def load(rel):
    with (ROOT/rel).open(encoding='utf-8') as f: return json.load(f)
def has_all(container, required):
    text=' '.join(str(x) for x in container).lower(); return all(x.lower() in text or x.lower().replace('_',' ') in text for x in required)
def validate_policy():
    ok=True; d=load(POLICY)
    if d.get('status')!='governed_non_public_static_workbench_public_readiness_boundary_policy': error('policy invalid status'); ok=False
    if d.get('maturity')!=MATURE: error('policy invalid maturity'); ok=False
    if d.get('current_baseline_status')!='locked_validated_internal_static_non_public_non_operational_visual_baseline': error('policy invalid baseline status'); ok=False
    if 'prerequisite-definition layer only' not in d.get('public_readiness_definition','').lower(): error('policy definition must be prerequisite-definition layer only'); ok=False
    if not has_all(d.get('prohibited_actions',[]),PROHIBITED): error('policy missing prohibited actions'); ok=False
    if not has_all(d.get('allowed_boundary_actions',[]),['public-readiness boundary definition','prerequisite definition','route blocker definition','risk boundary definition','non-authorization rule definition','future validation requirement definition','publisher gate update','reference gate update','validation only']): error('policy missing allowed actions'); ok=False
    if not has_all(d.get('non_authorization_rules',{}).get('blocked',[]),['public release','public route','sitemap','public navigation','public workbench','engine','classifier','upload','scoring','API','analytics','DNS','Cloudflare','custom domain launch','deployment','public tool behavior','prototype modification','prototype expansion','production readiness']): error('policy missing non-authorization rules'); ok=False
    if NUMERIC.search((ROOT/POLICY).read_text(encoding='utf-8')): error('policy contains numeric score/grade/percentage'); ok=False
    return ok
def validate_records():
    ok=True
    na=load('data/non-public-static-workbench-public-readiness-non-authorization-rules-v1.json')
    if not set(BLOCKED).issubset(set(na.get('blocked_authorizations',[]))): error('non-authorization missing blocked_authorizations'); ok=False
    if not set(['public_readiness_validation','public_copy_boundary_governance','public_route_eligibility_governance','public_indexing_policy_governance','public_disclaimer_governance','public_accessibility_review','public_security_privacy_review','public_deployment_gate_review']).issubset(set(na.get('allowed_future_discussion_only',[]))): error('non-authorization missing discussion-only items'); ok=False
    if not has_all(na.get('enforcement_notes',[]),['not public-readiness validation','not public route approval','not engine approval','not upload/scoring approval','not deployment approval','custom domain launch remains separately governed']): error('non-authorization missing enforcement notes'); ok=False
    pre=load('data/non-public-static-workbench-public-readiness-required-prerequisites-v1.json')
    if not set(PREREQS).issubset(set(pre.get('required_prerequisites',[]))): error('prerequisites missing required items'); ok=False
    missing=[x for x in PREREQS if x not in ['baseline_lock_validation_complete','public_readiness_boundary_governance_complete']]
    if not set(missing).issubset(set(pre.get('missing_prerequisites',[]))): error('prerequisites missing missing_prerequisites'); ok=False
    if not has_all(pre.get('prerequisite_boundary',[]),['do not authorize public release','do not authorize public route','do not authorize engine/classifier/upload/scoring','define the future chain only']): error('prerequisite boundary incomplete'); ok=False
    risk=load('data/non-public-static-workbench-public-readiness-risk-boundary-v1.json')
    if not set(RISKS).issubset(set(risk.get('public_risk_items',[]))): error('risk boundary missing risks'); ok=False
    if not has_all(risk.get('required_future_mitigations',[]),['public disclaimer governance','public copy boundary','public route eligibility review','no operation notice','artifact-subject separation notice','not-assessable explanation','no fake-real language audit','no upload/scoring implication audit','public SEO snippet governance','screenshot/context language consideration']): error('risk boundary missing mitigations'); ok=False
    if not has_all(risk.get('blocked_interpretations',[]),['Hoax.ai is a detector','Hoax.ai verifies truth','Hoax.ai classifies people or institutions','Not Assessable means fake','output envelope is a verdict','public prototype is an engine','visual workbench is a product launch']): error('risk boundary missing blocked interpretations'); ok=False
    rb=load('data/non-public-static-workbench-public-readiness-route-blockers-v1.json')
    if not set(['no_public_workbench_route','prototype_not_registered_as_public_route','prototype_not_in_sitemap','prototype_not_publicly_linked']).issubset(set(rb.get('current_route_status',[]))): error('route blockers missing current route status'); ok=False
    if not set(ROUTE_BLOCKERS).issubset(set(rb.get('route_blockers',[]))): error('route blockers missing blockers'); ok=False
    if not has_all(rb.get('required_future_route_gates',[]),['public_readiness_boundary_validation','public_route_eligibility_governance','public_copy_boundary_governance','public_disclaimer_governance','public_indexability_decision','public_accessibility_audit','public_security_privacy_review','route_registry_governance','sitemap_eligibility_governance','validate_all_pass']): error('route blockers missing future route gates'); ok=False
    return ok
def validate_audit():
    ok=True; a=load('data/non-public-static-workbench-public-readiness-boundary-audit-v1.json')
    if a.get('overall_outcome')!='non_public_static_workbench_public_readiness_boundary_governance_validated': error('audit invalid outcome'); ok=False
    groups={'baseline_status_results':['locked_visual_baseline_validated','prototype_files_not_modified','prototype_remains_internal','prototype_remains_static','prototype_remains_non_public','prototype_remains_non_operational'],'boundary_results':['public_readiness_defined_as_boundary_only','public_readiness_does_not_authorize_release','public_readiness_does_not_authorize_route','public_readiness_does_not_authorize_engine','public_readiness_does_not_authorize_classifier','public_readiness_does_not_authorize_upload','public_readiness_does_not_authorize_scoring'],'route_blocker_results':['route_blockers_defined','route_eligibility_not_granted','sitemap_eligibility_not_granted','public_navigation_not_granted'],'public_surface_results':['no_route_registry_entry','no_sitemap_entry','no_homepage_link','no_public_reference_links','no_language_page_link','no_public_navigation','public_surface_unchanged_four_urls'],'capability_block_results':['no_engine','no_classifier','no_detector','no_upload','no_scoring','no_fake_real','no_api','no_analytics','no_storage','no_network_calls','no_deployment_change'],'python_cache_results':['no_pycache_tracked','no_pyc_staged','no_python_cache_committed']}
    for k,req in groups.items():
        if not set(req).issubset(set(a.get(k,[]))): error(f'audit missing {k}'); ok=False
    return ok
def validate_files_public():
    ok=True
    if not all((ROOT/x).is_file() for x in LOCKED_FILES): error('prototype files missing'); return False
    if {x.name for x in PROTO_DIR.iterdir() if x.is_file()}!={'index.html','prototype.css'}: error('prototype dir has extra files'); ok=False
    if subprocess.run(['git','diff','--name-only','--',*LOCKED_FILES],cwd=ROOT,text=True,capture_output=True).stdout.strip(): error('prototype files modified'); ok=False
    if subprocess.run(['git','diff','--cached','--name-only','--',*LOCKED_FILES],cwd=ROOT,text=True,capture_output=True).stdout.strip(): error('prototype files staged'); ok=False
    routes=load('data/route-registry.json').get('routes',[])
    if not validate_public_surface(routes,error,PUBLIC_SITEMAP_URL_COUNT): ok=False
    if 'evidence-posture-workbench' in json.dumps(routes).lower() or 'internal_prototypes' in json.dumps(routes).lower(): error('prototype registered as route'); ok=False
    locs=[e.text.strip().lower() for e in ET.parse(ROOT/'sitemap.xml').findall('.//{*}loc') if e.text]
    if len(locs)!=PUBLIC_SITEMAP_URL_COUNT or any('evidence-posture-workbench' in x or 'internal_prototypes' in x for x in locs): error('sitemap mismatch or prototype leak'); ok=False
    pat=re.compile(r'internal_prototypes|evidence-posture-workbench',re.I)
    for rel in ['index.html','reference/evidence-posture/index.html','reference/artifact-subject-separation/index.html','language/index.html']:
        if pat.search((ROOT/rel).read_text(encoding='utf-8')): error(f'{rel} links to prototype'); ok=False
    if (ROOT/'.nojekyll').exists(): error('.nojekyll exists'); ok=False
    return ok
def validate_governance():
    ok=True; pub=load('data/publisher-governance-policy.json')
    if pub.get('current_publisher_status') not in (PUBLISHER_STATUS_POST_NON_PUBLIC_STATIC_WORKBENCH_PUBLIC_READINESS_BOUNDARY_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE, PUBLISHER_STATUS_POST_PUBLIC_ROUTE_ELIGIBILITY_GOVERNANCE_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE, PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_ASSESSMENT_GOVERNANCE_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE, PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRY_GOVERNANCE_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE, PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_GOVERNANCE_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_ROUTE_CANDIDATE_REGISTRATION_AUTHORIZATION_GOVERNANCE, PUBLISHER_STATUS_GOVERNANCE_SCAFFOLDING_FREEZE, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PRODUCTION_BATCH_1, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PRODUCTION_BATCH_2, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PRODUCTION_BATCH_3, PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_STANDARD_V1, PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_PROTOCOL_V1_DRAFT, PUBLISHER_STATUS_POST_PUBLIC_INTERFACE_THESIS_EVIDENCE_FIELD, PUBLISHER_STATUS_POST_EVIDENCE_FIELD_STATIC_INTERFACE_EMBODIMENT_V1, PUBLISHER_STATUS_POST_EVIDENCE_FIELD_VISUAL_SYSTEM_ACCESSIBILITY_HARDENING, PUBLISHER_STATUS_POST_CONTROLLED_DOMAIN_CONNECTION_DECISION, PUBLISHER_STATUS_POST_ENGINE_BOUNDARY_AND_PUBLIC_REFERENCE_SEO_AUTHORITY_MAP, PUBLISHER_STATUS_POST_EVIDENCE_POSTURE_ENGINE_MODEL_V0, PUBLISHER_STATUS_POST_OUTPUT_LANGUAGE_GUARDRAIL_MODEL_V1, PUBLISHER_STATUS_POST_INTERNAL_NON_PUBLIC_ENGINE_PROTOTYPE_CHARTER, PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_IMPLEMENTATION_SPRINT, PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_VALIDATION, PUBLISHER_STATUS_POST_CONTROLLED_INTERNAL_PROTOTYPE_V0_HARDENING_VALIDATION, PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_TRACEABILITY_INTERPRETABILITY_AUDIT_VALIDATION, PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_FIXTURE_COVERAGE_MATRIX_VALIDATION, PUBLISHER_STATUS_POST_TARGETED_SYNTHETIC_FIXTURE_EXPANSION_V1_VALIDATION, PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_COMPOUND_BOUNDARY_STRESS_TEST_VALIDATION, PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_GUARDRAIL_RED_TEAM_PACK_VALIDATION, PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_OUTPUT_ADMISSIBILITY_CONTRACT_VALIDATION, PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_ADMISSIBILITY_REGRESSION_SUITE_VALIDATION, PUBLISHER_STATUS_POST_INTERNAL_PROTOTYPE_RELEASE_BLOCKER_BOARD_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_EXPOSURE_PREREQUISITE_MAP_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_COPY_BOUNDARY_FRAMEWORK_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_EVIDENCE_RISK_UTILITY_SURFACE_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ROUTE_EXPANSION_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_UTILITY_INTERFACE_EMBODIMENT_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_AUTHORITY_INTERNAL_LINKING_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SOURCE_CONFIDENCE_LAYER_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ANSWER_SURFACE_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_CITATION_RETRIEVAL_HARDENING_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_QUALITY_CONSOLIDATION_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_DEPTH_EXPANSION_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_PATHWAY_PAGES_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_NAVIGATION_IA_CONSOLIDATION_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SURFACE_AUTHORITY_REVIEW_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_ENTRY_POINTS_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_NARRATIVE_SURFACE_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_ACQUISITION_READINESS_SURFACE_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_SURFACE_CONSOLIDATION_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_RELEASE_INTEGRITY_AUDIT_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXTERNAL_REVIEW_READINESS_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEWER_PACKET_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_REVIEW_PACKET_INTEGRITY_AUDIT_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_SURFACE_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_EXECUTIVE_OVERVIEW_INTEGRITY_AUDIT_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_STRATEGIC_REVIEW_INDEX_INTEGRITY_AUDIT_VALIDATION, PUBLISHER_STATUS_POST_PUBLIC_REFERENCE_SYSTEM_MAP_SURFACE_VALIDATION): error('publisher status invalid'); ok=False
    gate=next((g for g in load('data/publisher-quality-gates.json').get('gates',[]) if g.get('name')=='Non-Public Static Workbench Public-Readiness Boundary Governance Gate'),None)
    if not gate: error('public-readiness boundary governance gate missing'); ok=False
    else:
        for f in ['required_before_non_public_static_workbench_public_readiness_boundary_validation','required_before_public_route_eligibility_governance','required_before_any_public_workbench_route','required_before_engine_governance']:
            if gate.get(f) is not True: error(f'gate {f} must be true'); ok=False
        if gate.get('bypassable') is not False: error('gate bypassable'); ok=False
        if not has_all([gate.get('notes','')],['public engine','public classifier','public tool','public route','sitemap','navigation','upload','scoring','API','forms','analytics','deployment','DNS','Cloudflare','custom domain launch']): error('gate notes incomplete'); ok=False
    exp=load('data/reference-expansion-gate.json'); checks=' '.join(exp.get('required_pre_release_checks',[])).lower(); rules=' '.join(exp.get('release_eligibility_rules',[])).lower()
    if 'public_readiness_boundary_governance' not in checks: error('reference gate missing boundary governance'); ok=False
    if 'no_public_engine_eligibility_by_public_readiness_boundary_governance_alone' not in rules: error('reference gate grants engine eligibility'); ok=False
    locs={s.get('location') for s in load('data/source-registry.json').get('sources',[])}
    for loc in SOURCE_LOCS:
        if loc not in locs: error(f'source registry missing {loc}'); ok=False
    if not any(c.get('claim_id')=='CLAIM-0048' for c in load('data/evidence-ledger.json').get('claims',[])): error('CLAIM-0048 missing'); ok=False
    if not any(c.get('claim_id')=='CLAIM-0048' for c in load('data/claim-source-map.json').get('claim_source_links',[])): error('CLAIM-0048 map missing'); ok=False
    if 'validate_non_public_static_workbench_public_readiness_boundary_governance.py' not in (ROOT/'validators'/'validate_all.py').read_text(encoding='utf-8'): error('validate_all missing sprint42 validator'); ok=False
    if 'DEC-060' not in (ROOT/'DECISION_LOG.md').read_text(encoding='utf-8'): error('DEC-060 missing'); ok=False
    return ok
def validate_cache():
    names=subprocess.run(['git','ls-files'],cwd=ROOT,text=True,capture_output=True).stdout.splitlines()+subprocess.run(['git','diff','--cached','--name-only'],cwd=ROOT,text=True,capture_output=True).stdout.splitlines()
    for rel in names:
        low=rel.lower().replace('\\','/')
        if '__pycache__/' in low or low.endswith(('.pyc','.pyo','.pyd')) or '.pytest_cache/' in low: error('python cache tracked/staged'); return False
    return True
def main():
    parse=['data/non-public-static-workbench-public-readiness-boundary-policy.json','data/non-public-static-workbench-public-readiness-non-authorization-rules-v1.json','data/non-public-static-workbench-public-readiness-required-prerequisites-v1.json','data/non-public-static-workbench-public-readiness-risk-boundary-v1.json','data/non-public-static-workbench-public-readiness-route-blockers-v1.json','data/non-public-static-workbench-public-readiness-boundary-audit-v1.json','data/non-public-static-workbench-visual-system-baseline-lock-validation-results-v1.json','data/non-public-static-workbench-visual-system-baseline-record-validation-v1.json','data/non-public-static-workbench-visual-system-change-control-validation-v1.json','data/publisher-governance-policy.json','data/publisher-quality-gates.json','data/reference-expansion-gate.json','data/route-registry.json']
    for rel in parse:
        try: load(rel)
        except Exception as e: error(f'{rel} parse failed: {e}'); return 1
    for rel in ['sitemap.xml','index.html','reference/evidence-posture/index.html','reference/artifact-subject-separation/index.html','language/index.html',*LOCKED_FILES]:
        if not (ROOT/rel).is_file(): error(f'{rel} missing'); return 1
    try: ET.parse(ROOT/'sitemap.xml')
    except ET.ParseError as e: error(f'sitemap parse failed {e}'); return 1
    ok=all(fn() for fn in [validate_policy,validate_records,validate_audit,validate_files_public,validate_governance,validate_cache])
    if ok: print('PASS'); return 0
    return 1
if __name__=='__main__': sys.exit(main())
