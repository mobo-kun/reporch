#!/usr/bin/env python3
"""Build references/analyses.json and references/analyses.md from the catalogue source.

Source: tools/catalogue_source.md (the human-edited tables) + NEEDS below (machine field keys).
A need "a|b" means either field is enough. Run after editing either, then run the tests.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

NEEDS = {
 "A1": "task_success", "A2": "success_level|assisted", "A3": "task_time", "A4": "errors",
 "A5": "post_task_rating", "A6": "paths|first_click", "A7": "steps_reached", "A8": "paths",
 "A9": "task_success|task_time, segment", "A10": "attempts", "A11": "recall|returning_performance",
 "A12": "element_comprehension", "A13": "issues, issue_time_lost", "A14": "task_time, time_threshold",
 "A15": "action_counts, optimal_actions", "A16": "pages_visited, optimal_actions",
 "A17": "task_success, task_time", "A18": "issues, issue_task", "A19": "pre_task_expectation, post_task_rating",
 "A20": "task_time|action_counts, expert_benchmark", "A21": "nav_method",
 "B1": "sus_items", "B2": "nps_score", "B3": "satisfaction_rating", "B4": "standard_scale_items",
 "B5": "likert_items", "B6": "attribute_ratings", "B7": "intent_rating", "B8": "segment, sus_items|nps_score|satisfaction_rating|standard_scale_items|likert_items",
 "B9": "preference_choice", "B10": "reaction_words", "B11": "effort_rating",
 "C1": "survey_export", "C2": "choice_question", "C3": "multi_choice_question", "C4": "two_categorical",
 "C5": "ranking_question", "C6": "open_text", "C7": "demographics", "C8": "awareness_items",
 "C9": "awareness_items, usefulness_items",
 "D1": "transcripts|notes", "D2": "issues, issue_participant, issue_severity", "D3": "issues, issue_severity",
 "D4": "transcripts", "D5": "transcripts, observations", "D6": "stage_notes", "D7": "behaviour_notes",
 "D8": "transcripts|notes, goals", "D9": "diary_entries", "D10": "transcripts|survey_export, observations",
 "D11": "coded_remarks|transcripts", "D12": "incidents", "D13": "issues, locale", "D14": "issues, issue_severity|issue_iteration",
 "D15": "issues, issue_participant", "D16": "issues, issue_category",
 "E1": "step_counts", "E2": "session_outcomes", "E3": "coded_sessions", "E4": "device",
 "E5": "variant_results", "E6": "two_periods", "E7": "click_counts", "E8": "feature_usage_log",
 "E9": "error_log", "E10": "feedback_tickets", "E11": "wait_times", "E12": "eye_tracking", "E13": "physiological",
 "F1": "card_sort_open", "F2": "card_sort_open", "F3": "evaluator_issues", "F4": "competitor_features",
 "F5": "competitor_notes", "F6": "evaluator_issues, multiple_evaluators", "F7": "competitor_metrics",
 "F8": "card_sort_open", "F9": "card_sort_closed", "F10": "accessibility_audit",
 "G1": "participants", "G2": "participants", "G3": "findings, solutions", "G4": "findings",
 "G5": "recommendations_rated", "G6": "cleaned_data", "G7": "targets", "G8": "issues, issue_participant",
 "G9": "iterations", "G10": "costs", "G11": "metric_weights, task_success|task_time|satisfaction_rating",
 "G12": "multiple_designs", "G13": "task_success, task_time, errors, satisfaction_rating|post_task_rating",
 "G14": "task_success, post_task_rating|satisfaction_rating", "G15": "metrics_list", "G16": "time_series",
 "G17": "findings, heart_tags",
 "H1": "stage_counts", "H2": "north_star", "H3": "signups, key_action_events", "H4": "signups, key_action_events",
 "H5": "activity_by_date", "H6": "users_by_period", "H7": "daily_monthly_actives", "H8": "feature_use_per_user",
 "H9": "revenue", "H10": "revenue, acquisition_costs, users_by_period", "H11": "channel_traffic",
 "H12": "referrals", "H13": "events_per_user", "H14": "billing_events", "H15": "feature_use_per_user, usage_threshold",
 "H16": "referral_question|referrals",
 "I1": "onboarding_steps", "I2": "signups, key_action_events", "I3": "onboarding_steps, activity_by_date",
 "I4": "onboarding_screens", "I5": "guidance_events",
}
ALWAYS = ["G1", "G2"]  # included whenever numbers are reported

GROUPS = {"A": "Task performance", "B": "Questionnaires and scores", "C": "Surveys",
          "D": "Qualitative", "E": "Behaviour data", "F": "Card sorting, heuristics, competition, accessibility",
          "G": "Across the study", "H": "Product metrics and growth", "I": "Onboarding"}


def parse(md):
    rows = []
    for line in md.splitlines():
        m = re.match(r"^\| ([A-I]\d+) \| (.+?) \| (.+?) \| (.+?) \| (.*?) \|$", line)
        if m:
            i, title, needs_text, output, source = (x.strip() for x in m.groups())
            rows.append({"id": i, "group": GROUPS[i[0]], "title": title, "needsText": needs_text,
                         "output": output, "sources": [s.strip() for s in source.split(",") if s.strip() not in ("—", "")],
                         "needs": [n.strip() for n in NEEDS[i].split(",")]})
    return rows


def main():
    with open(os.path.join(HERE, "catalogue_source.md"), encoding="utf-8") as f:
        src = f.read()
    rows = parse(src)
    missing = set(NEEDS) - {r["id"] for r in rows}
    assert not missing, f"NEEDS for unknown ids: {missing}"
    fields = sorted({f for r in rows for n in r["needs"] for f in n.split("|")})
    out = {"schema": "reporch/catalogue@1", "always": ALWAYS, "fields": fields, "analyses": rows}
    with open(os.path.join(ROOT, "references", "analyses.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "references", "analyses.md"), "w", encoding="utf-8") as f:
        f.write("<!-- Generated from tools/catalogue_source.md by tools/build_catalogue.py -->\n" + src)
    print(len(rows), "analyses,", len(fields), "fields")


if __name__ == "__main__":
    main()
