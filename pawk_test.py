from pawk import Action


def test_action_parse():
    action = Action(r'/(\w+)/ l')
    assert action.pattern.pattern == r'(\w+)'
    assert action.cmd == 'l'
    assert action.negate is False


def test_action_match():
    action = Action(r'/(\w+) \w+/')
    groups = action.match('test case')
    assert groups == ('test',)


def test_action_match_negate():
    action = Action(r'!/(\w+) \w+/')
    groups = action.match('test case')
    assert groups is None
    groups = action.match('test')
    assert groups == ()
