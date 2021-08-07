from parser.utils import _comment_remover


def test_comment_remover():
    assert _comment_remover("") == ""
    assert _comment_remover("'ddw'") == "'ddw'"
    assert _comment_remover("123") == "123"
    assert _comment_remover("123//") == "123"
    assert _comment_remover("123/") == "123/"
    assert _comment_remover("123  /") == "123  /"
    assert _comment_remover("  // wdwdw") == "  "
    assert _comment_remover("  / / wdwdw") == "  / / wdwdw"
    assert _comment_remover(" sws / / wdwdw") == " sws / / wdwdw"
    assert _comment_remover(" sws \"\" / / wdwdw") == " sws \"\" / / wdwdw"
    assert _comment_remover(" sws \"wow\" / / wdwdw") == " sws \"wow\" / / wdwdw"
    assert _comment_remover(" sws \"\" // wdwdw") == " sws \"\" "
    assert _comment_remover(" sws \"22\" // wdwdw") == " sws \"22\" "
    assert _comment_remover(" sws \'   \' // wdwdw") == " sws \'   \' "
    assert _comment_remover(" sws \'   \' // wdwdw \"test\"") == " sws \'   \' "
