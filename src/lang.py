import gettext

langs = {
    'en': gettext.NullTranslations(),
    'es': gettext.translation('chessd', languages=['es'], localedir='./locale'),
    'compat': gettext.translation('chessd', languages=['compat'], localedir='./locale')
}


# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
