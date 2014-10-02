# -*- coding: utf-8 -*-
import re
import codecs
import locale
import logging

import clime

def get_or_null(src_dict, key, default=u''):
    if src_dict[key]:
        return src_dict[key]
    else:
        return default

def __dbg_return(val, msg):
    print msg
    return val

def jap_strcoll(str1, str2):
    separate_symbols = u'［］―・∘、＝-()'

    if str1 == str2:
        return 0
    elif not str1 and str2:
        return -1
    elif str1 and not str2:
        return 1
    else:
        for c in separate_symbols:
            str1 = str1.replace(c, u'')
            str2 = str1.replace(c, u'')

        try:
            for i in range(len(str1)):
                if str1[i] > str2[i]:
                    return 1
                elif str1[i] < str2[i]:
                    return -1

            return 0
        except KeyError:
            return 1

def main(filename, outfile='tabfile', delimit=None):
    sep_key = u'<INDENT=1>'
    sep_def = u'<INDENT=4>'

    with codecs.open(filename, 'r', encoding='utf-8') as fh:
        items = re.findall(ur'<INDENT=1>[^\*]*ENDL\*', fh.read(), re.MULTILINE)

    ## numeric index of dictionary items
    index = 0
    dictionary = []

    ## for debug purpose, delimit the number of items
    delimited = items
    if delimit:
        delimited = items[:delimit]

    for item in delimited:
        lines = item.split(u'\n')

        key = u''
        key_raw = u''
        val = []
        meta_dict = {}
        for l in lines[:-1]:
            if l.startswith(sep_key):
                key_raw = l.replace(sep_key, u'')

                ## unicode symbols used in items
                separate_symbols = u'［］―・∘、＝-()'
                unicode_char = ur'［］―・∘、＝\w\- ()'

                pattern = []
                pattern.append(ur'<HEAD>(?P<hira>[%s（）]+)</HEAD>' % unicode_char)
                pattern.append(ur'(?P<kata>[%s]+)?' % unicode_char)
                pattern.append(ur'((?P<accent>\[[0-9]+\]))?')
                pattern.append(ur'((?P<accent2>\[[0-9]+\]))?')
                pattern.append(ur'((?P<accent3>\[[0-9]+\]))?')
                pattern.append(ur'((?P<kanji>【[%s（）]+】))?' % unicode_char)
                pattern.append(ur'((?P<kanji2>〖[%s（）]+〗))?' % unicode_char)
                pattern.append(ur'((?P<part>（[%s\[\]]+）[%s\[\]]*))?' % (unicode_char, unicode_char))

                pattern = ur'[ ]*'.join(pattern)

                m = re.search(pattern, key_raw, re.UNICODE)

                ## extract yomi
                yomi = m.groupdict()['hira']
                for sym in separate_symbols:
                    yomi = yomi.replace(sym, u'')

                ## display key
                key = u''.join(
                    [m.groupdict()['hira'],
                     (lambda x: u',%s' % x if x else u'')(m.groupdict()['kanji']),
                     (lambda x: x if x else u'')(m.groupdict()['kanji2']),
                ])

                try:
                    logging.info(u"key=%s" % key)
                except:
                    pass

                meta_dict = m.groupdict()

                val.append(u' '.join([p for p in [
                    get_or_null(meta_dict, 'hira'),
                    get_or_null(meta_dict, 'kata'),
                    get_or_null(meta_dict, 'accent'),
                    get_or_null(meta_dict, 'accent2'),
                    get_or_null(meta_dict, 'accent3'),
                    get_or_null(meta_dict, 'kanji'),
                    get_or_null(meta_dict, 'kanji2'),
                    get_or_null(meta_dict, 'part')
                ] if p]
                ))
            elif l.startswith(sep_def):
                val.append(u'%s' % l.replace(sep_def, u''))
            elif l == 'ENDL*':
                pass
            else:
                val.append(u'%s' % l)

        dictionary.append({
            'yomi': yomi,
            'key': key,
            'val': u'<p>'.join(val),
            'meta': meta_dict
        })

    ## sort items alphabetically
    locale.setlocale(locale.LC_ALL, "ja_JP.UTF-8")
    dictionary.sort(
        #cmp=locale.strcoll,
        cmp=jap_strcoll,
        key=lambda x:x['yomi']
    )
    for p in dictionary:
        print p['key']

    with codecs.open(outfile, 'w+', encoding='utf-8') as fh:
        for item in dictionary:
            try:
                fh.write(u"%s\t%s\n" % (
                    item['key'], item['val'])
                )
            except Exception, e:
                pass

if __name__ == '__main__':
    clime.Program(debug=True).main()
