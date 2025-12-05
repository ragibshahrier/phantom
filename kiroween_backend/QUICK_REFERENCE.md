# Phantom AI Quick Reference Card

## 🚀 Quick Start

```bash
# Run all tests
cd kiroween_backend
source venv/bin/activate
python run_all_intelligent_tests.py

# Start server
python manage.py runserver
```

## 📝 Example User Inputs

| Input | What Phantom Does |
|-------|-------------------|
| "I have a math exam on Friday" | Creates exam + 2-3 study sessions, clears conflicts |
| "Need to work out" | Creates gym session (1 hour, morning/evening) |
| "Meeting Sarah tomorrow" | Creates social event (2 PM, 2 hours) |
| "I'm too tired to study" | Cancels current session, reshuffles week |

## 🎯 Priority Hierarchy

```
5 → Exam     (Never compromised)
4 → Study    (Preserved over lower)
3 → Gym      (Rescheduled if needed)
2 → Social   (Deleted for exam prep)
1 → Gaming   (Deleted for exam prep)
```

## ⏰ Intelligent Defaults

| Category | Default Time | Default Duration |
|----------|-------------|------------------|
| Exam | 9 AM | 2-3 hours |
| Study | 6 PM | 2 hours |
| Gym | 7 AM or 6 PM | 1 hour |
| Social | 2 PM | 2-3 hours |
| Gaming | 6 PM | 1-2 hours |

## 🧪 Test Commands

```bash
# All tests
python run_all_intelligent_tests.py

# Intelligent scheduling
python manage.py test ai_agent.test_intelligent_scheduling

# Chat endpoint
python manage.py test ai_agent.test_chat_endpoint_integration

# Single test
python manage.py test ai_agent.test_intelligent_scheduling.IntelligentSchedulingTestCase.test_exam_creates_study_sessions
```

## 📊 Test Coverage

- ✅ 25+ tests
- ✅ 6 coverage areas
- ✅ 100% expected pass rate
- ✅ CREATE, UPDATE, DELETE, RESHUFFLE operations
- ✅ Priority enforcement
- ✅ Context awareness

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | `pip install -r requirements.txt` |
| Database errors | `python manage.py migrate` |
| Missing categories | `python manage.py populate_categories` |
| Test failures | Check `TESTING_GUIDE.md` |

## 📁 Key Files

| File | Purpose |
|------|---------|
| `ai_agent/prompts.py` | Enhanced system prompts |
| `ai_agent/agent.py` | Agent with context |
| `ai_agent/views.py` | Chat API endpoint |
| `test_intelligent_scheduling.py` | Integration tests |
| `test_chat_endpoint_integration.py` | API tests |

## 🎭 Victorian Phrases

- "I have taken the liberty of..."
- "Most certainly, at your service"
- "I shall attend to that forthwith"
- "Most excellent!"
- "I beg your pardon, but..."

## ✅ Verification

```bash
# Verify enhancement loaded
python test_phantom_enhancement.py

# Check all tests pass
python run_all_intelligent_tests.py

# Start server
python manage.py runserver
```

## 📖 Documentation

- `PHANTOM_AI_ENHANCEMENT.md` - Complete enhancement docs
- `INTELLIGENT_SCHEDULING_TESTS.md` - Test suite docs
- `TESTING_GUIDE.md` - Comprehensive testing guide
- `COMPLETE_IMPLEMENTATION_SUMMARY.md` - Full summary

## 🎉 Success Indicators

- ✅ All tests pass
- ✅ Agent understands implicit needs
- ✅ Events created automatically
- ✅ Priorities enforced
- ✅ Conflicts resolved
- ✅ Victorian style maintained

---

**Quick Help:** Check `TESTING_GUIDE.md` for detailed information
