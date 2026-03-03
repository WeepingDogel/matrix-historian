#!/usr/bin/env python3
"""
Validate GitHub Actions workflow structure
"""

import sys

import yaml


def main():
    with open(".github/workflows/ci.yml", "r") as f:
        workflow = yaml.safe_load(f)

    print("=== GitHub Actions Workflow Validation ===")
    print(f"Workflow: {workflow.get('name', 'Unnamed')}")

    # Check jobs
    jobs = workflow.get("jobs", {})
    print(f"\nJobs found: {len(jobs)}")

    job_summary = []
    for job_name, job_config in jobs.items():
        job_info = {
            "name": job_name,
            "runner": job_config.get("runs-on", "N/A"),
            "steps": len(job_config.get("steps", [])),
            "needs": job_config.get("needs", []),
        }
        job_summary.append(job_info)

    # Print job details
    for job in job_summary:
        print(f"\n  {job['name']}:")
        print(f"    Runner: {job['runner']}")
        print(f"    Steps: {job['steps']}")
        if job["needs"]:
            print(f"    Depends on: {job['needs']}")

    # Check for critical jobs
    critical_jobs = ["lint-and-format", "test", "build-and-push"]
    missing = [job for job in critical_jobs if job not in jobs]

    if missing:
        print(f"\n⚠️  Missing critical jobs: {missing}")
    else:
        print(f"\n✅ All critical jobs present")

    print("\n=== Validation Complete ===")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"❌ Validation error: {e}")
        sys.exit(1)
