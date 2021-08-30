def filterHTMLtable(htmltable):

    lines = htmltable\
        .replace('  ', '')\
        .replace('\\x00', '')\
        .replace('\\r', '')\
        .replace('\\x', '')\
        .split('\\n')

    opentag = False
    HTML = ''
    strHTML= ''
    for line in lines:

        HTML = HTML + line

        while True:
            if opentag:

                endtag = HTML.find('>')+1
                tag = HTML[:endtag-1].split(' ')[0].lower()
                opentag = False
                HTML = HTML[endtag:]

                if (tag =='table') or (tag=='th') or (tag == 'td') or (tag == 'tr'):
                    strHTML = strHTML + f'<{tag}>'

            elif '<' in HTML:
                starttag = HTML.find('<')
                closetag = HTML.find('</')

                if (starttag < closetag) or (closetag < 0):
                    HTML = HTML[starttag+1:]
                    opentag = True

                elif closetag == starttag:
                    endtag = HTML.find('>') + 1
                    tag = HTML[:endtag].lower()

                    if ('table' in tag) or ('th' in tag) or ('td' in tag) or ('tr' in tag):
                        HTML = HTML[endtag:]
                        strHTML = strHTML + tag + '\n'
                    else:
                        HTML = HTML[:closetag] + HTML[endtag:]
            else:
                break

    return strHTML