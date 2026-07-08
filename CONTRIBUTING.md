# Contributing to PicoClaw Skills Library

Thank you for contributing to the distributed mesh network! Every skill you add helps the collective intelligence grow.

## Skill Requirements

1. **North Star Alignment:** All skills must advance one of:
   - Revenue generation (Phase 1)
   - Autonomous operation (Phase 2)
   - Intelligence synthesis (Phase 3)
   - R&D for the medical ENDS device (Phases 4-7)

2. **Manifest File:** Every skill MUST include a `manifest.json`:
   ```json
   {
     "name": "your_skill_name",
     "tier": 1,
     "category": "revenue|autonomy|intelligence|mod_project",
     "entry_point": "skills/your_skill/main.py",
     "env_requirements": ["package1", "package2"],
     "node_type": ["spoke-compute", "spoke-revenue"],
     "inputs": ["input1", "input2"],
     "outputs": ["output1", "output2"],
     "north_star_aligned": true,
     "phase_gate": "phase_1_revenue_foundation"
   }
   ```

3. **Code Quality:**
   - Python 3.8+ compatible
   - No hardcoded credentials (use `.env` or config)
   - Graceful degradation if dependencies missing
   - Logging to `~/.picoclaw/logs/`

4. **Privacy:**
   - Local data stays local
   - Only insights/analytics flow upstream
   - User consent required for any data sharing

## Submission Process

1. Fork `q-u-i-l-l-y/picoclaw-skills`
2. Create your skill in `/skills/your_skill_name/`
3. Add `manifest.json` and `README.md`
4. Test on your local node: `python3 skills/your_skill_name/main.py --test`
5. Submit PR with description of North Star alignment

## Review Criteria

| Criteria | Weight |
|----------|--------|
| North Star alignment | 40% |
| Code quality | 25% |
| Documentation | 20% |
| Privacy compliance | 15% |

## Reward Structure

Contributors earn reputation in the mesh:
- **Skill merged:** +100 rep points
- **Bug fix:** +25 rep points
- **Documentation:** +10 rep points
- **High-rep contributors** get priority for R&D fund allocations

---

**Remember:** *Clone the repo, become a node. Build skills, advance the vision.*
