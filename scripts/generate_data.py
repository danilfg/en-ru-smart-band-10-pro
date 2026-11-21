#!/usr/bin/env python3
"""Compile editor-friendly, manually curated EN-RU TSV into compact offline Vela data."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
IRREGULAR = {
    'be': ('was/were','been'), 'have': ('had','had'), 'do': ('did','done'),
    'say': ('said','said'), 'go': ('went','gone'), 'get': ('got','gotten'),
    'make': ('made','made'), 'know': ('knew','known'), 'think': ('thought','thought'),
    'take': ('took','taken'), 'see': ('saw','seen'), 'come': ('came','come'),
    'find': ('found','found'), 'give': ('gave','given'), 'tell': ('told','told'),
    'feel': ('felt','felt'), 'become': ('became','become'), 'leave': ('left','left'),
    'put': ('put','put'), 'mean': ('meant','meant'), 'keep': ('kept','kept'),
    'let': ('let','let'), 'begin': ('began','begun'), 'bring': ('brought','brought'),
    'write': ('wrote','written'), 'sit': ('sat','sat'), 'stand': ('stood','stood'),
    'lose': ('lost','lost'), 'pay': ('paid','paid'), 'meet': ('met','met'),
    'set': ('set','set'), 'lead': ('led','led'), 'hold': ('held','held'),
    'run': ('ran','run'), 'hear': ('heard','heard'), 'show': ('showed','shown'),
    'build': ('built','built'), 'sleep': ('slept','slept'),
    'break': ('broke','broken'), 'catch': ('caught','caught'),
}
# Grammatical V1/V2/V3 examples for high-frequency standalone irregular verbs.
VERB_EXAMPLES = {
    'be': ['I am ready.', 'I was ready yesterday.', 'I have been ready all day.'],
    'have': ['I have a question.', 'I had a question.', 'I have had this question before.'],
    'do': ['I do my homework.', 'I did my homework.', 'I have done my homework.'],
    'say': ['I say hello.', 'I said hello.', 'I have said hello already.'],
    'go': ['I go home.', 'I went home.', 'I have gone home.'],
    'get': ['I get a message.', 'I got a message.', 'I have gotten a message.'],
    'make': ['I make a plan.', 'I made a plan.', 'I have made a plan.'],
    'know': ['I know the answer.', 'I knew the answer.', 'I have known the answer for years.'],
    'think': ['I think about work.', 'I thought about work.', 'I have thought about work.'],
    'take': ['I take the bus.', 'I took the bus.', 'I have taken the bus.'],
    'see': ['I see the sign.', 'I saw the sign.', 'I have seen the sign.'],
    'come': ['I come early.', 'I came early.', 'I have come early before.'],
    'find': ['I find errors.', 'I found an error.', 'I have found many errors.'],
    'give': ['I give her a book.', 'I gave her a book.', 'I have given her a book.'],
    'tell': ['I tell the truth.', 'I told the truth.', 'I have told the truth.'],
    'feel': ['I feel calm.', 'I felt calm.', 'I have felt calm all week.'],
    'become': ['I become stronger.', 'I became stronger.', 'I have become stronger.'],
    'leave': ['I leave at six.', 'I left at six.', 'I have left already.'],
    'put': ['I put the book here.', 'I put the book here yesterday.', 'I have put the book here.'],
    'mean': ['I mean it.', 'I meant it.', 'I have meant it all along.'],
    'keep': ['I keep a journal.', 'I kept a journal.', 'I have kept a journal for years.'],
    'let': ['I let her speak.', 'I let her speak yesterday.', 'I have let her speak.'],
    'begin': ['I begin with a question.', 'I began with a question.', 'I have begun with a question.'],
    'bring': ['I bring lunch.', 'I brought lunch.', 'I have brought lunch.'],
    'write': ['I write a letter.', 'I wrote a letter.', 'I have written a letter.'],
    'sit': ['I sit near the window.', 'I sat near the window.', 'I have sat there before.'],
    'stand': ['I stand outside.', 'I stood outside.', 'I have stood outside before.'],
    'lose': ['I lose my keys sometimes.', 'I lost my keys.', 'I have lost my keys.'],
    'pay': ['I pay by card.', 'I paid by card.', 'I have paid by card.'],
    'meet': ['I meet my friends.', 'I met my friends.', 'I have met my friends.'],
    'set': ['I set an alarm.', 'I set an alarm yesterday.', 'I have set an alarm.'],
    'lead': ['I lead the team.', 'I led the team.', 'I have led the team.'],
    'hold': ['I hold the bag.', 'I held the bag.', 'I have held the bag.'],
    'run': ['I run every morning.', 'I ran yesterday.', 'I have run this week.'],
    'hear': ['I hear music.', 'I heard music.', 'I have heard that song.'],
    'show': ['I show the result.', 'I showed the result.', 'I have shown the result.'],
    'build': ['I build apps.', 'I built an app.', 'I have built several apps.'],
    'sleep': ['I sleep well.', 'I slept well.', 'I have slept well this week.'],
}
TAILS = {
'GET': ['early','home','late','of the room','the bus','at the last stop','a bad cold','the exam','my colleagues','the mistake'],
'TAKE': ['a coat','the rubbish','the company','painting','my words','the news','the poster','a chair','my cat','my father'],
'LOOK': ['the number','my keys','the garden','the holidays','the issue','for traffic','at the photos','the shop','other people','my teacher'],
'GO': ['with the lesson','home','for dinner','for a walk','slowly','quickly','of the group','the list','a difficult period','at noon'],
'COME': ['home','early','tomorrow','during the meeting','for lunch','an old photo','with us','the stairs','a solution','in the end'],
'PUT': ['a coat','the meeting','the fire','a poster','the bag','the dishes','the book','the noise','a shelf','a new plan'],
'GIVE': ['too soon','the book','old clothes','to pressure','free samples','heat','new questions','with the task','on this game','to pedestrians'],
'MAKE': ['a story','the shape','the delay','old tools','the door is closed','to everyone','today','every week','another person','on time'],
'TURN': ['the device','the light','late','the offer','slowly','now','the page','a monster','fine','my teacher for help'],
'BRING': ['the topic','good memories','a new rule','the best in people','positive change','the cost','my friend','the team','the meeting','summer holidays'],
'HOLD': ['for a minute','the train','my emotions','my hand','until tomorrow','my job','the ticket','in a crisis','it against you','the decision'],
'KEEP': ['the pace','learning','from the fire','strangers','with friends','my spending','the children','during the meeting','the rule','until the end'],
'SET': ['a new phone','early','on a trip','some money','the tray','our work','in early','solving the problem','the design','a new release'],
'RUN': ['of patience','an old friend','fast','the instructions','the checklist','an idea by my boss','an article','a large bill','quickly','the dog'],
'MIXED': ['at the gym','the answer','the new app','on the road','last year','the package','a suitable jacket','with the exercise','the tests','the solution']
}
# Some phrases are separable or require a different grammatical subject.
PHRASE_OVERRIDES = {
    'make sense': ['This plan makes sense.', 'This plan made sense.', 'This plan has made sense from the start.'],
    'make sure': ['I make sure the door is closed.', 'I made sure the door was closed.', 'I have made sure the door is closed.'],
    'bring to mind': ['This brings to mind summer.', 'This brought to mind summer.', 'This has brought to mind summer.'],
    'hold against': ['I hold it against him.', 'I held it against him.', 'I have held it against him.'],
    'set in': ['Winter sets in early.', 'Winter set in early.', 'Winter has set in early.'],
    'keep in mind': ['I keep the rule in mind.', 'I kept the rule in mind.', 'I have kept the rule in mind.'],
    'run by': ['I run an idea by my boss.', 'I ran an idea by my boss.', 'I have run an idea by my boss.'],
    'give someone a hand': ['I give her a hand.', 'I gave her a hand.', 'I have given her a hand.'],
    'turn out': ['It turns out fine.', 'It turned out fine.', 'It has turned out fine.'],
    'go off': ['The alarm goes off early.', 'The alarm went off early.', 'The alarm has gone off early.'],
    'come up': ['An issue comes up.', 'An issue came up.', 'An issue has come up.'],
    'run out of': ['I run out of time.', 'I ran out of time.', 'I have run out of time.'],
    'give off': ['The heater gives off heat.', 'The heater gave off heat.', 'The heater has given off heat.'],
    'give way': ['I give way to pedestrians.', 'I gave way to pedestrians.', 'I have given way to pedestrians.'],
    'hold up': ['Traffic holds me up.', 'Traffic held me up.', 'Traffic has held me up.'],
    'keep an eye on': ['I keep an eye on the kids.', 'I kept an eye on the kids.', 'I have kept an eye on the kids.'],
    'make a decision': ['I make a decision.', 'I made a decision.', 'I have made a decision.'],
    'bring about': ['We bring about change.', 'We brought about change.', 'We have brought about change.'],
    'take off': ['I take off my coat.', 'I took off my coat.', 'I have taken off my coat.'],
    'turn on': ['I turn on the light.', 'I turned on the light.', 'I have turned on the light.'],
    'turn off': ['I turn off the light.', 'I turned off the light.', 'I have turned off the light.'],
    'turn down': ['I turn down the offer.', 'I turned down the offer.', 'I have turned down the offer.'],
    'put on': ['I put on a coat.', 'I put on a coat yesterday.', 'I have put on a coat.'],
    'put off': ['I put off the task.', 'I put off the task yesterday.', 'I have put off the task.'],
    'put away': ['I put away the dishes.', 'I put away the dishes yesterday.', 'I have put away the dishes.'],
    'take after': ['I take after my father.', 'I took after my father as a child.', 'I have always taken after my father.'],
    'come out': ['The book comes out in June.', 'The book came out last June.', 'The book has come out already.'],
    'come along': ['I come along with my friends.', 'I came along with my friends.', 'I have come along before.'],
    'come through': ['I come through when needed.', 'I came through when needed.', 'I have come through before.'],
    'make progress': ['I make progress every week.', 'I made progress last week.', 'I have made progress this month.'],
    'hold off': ['I hold off on the decision.', 'I held off on the decision.', 'I have held off on the decision.'],
    'hold down': ['I hold down a steady job.', 'I held down a steady job.', 'I have held down a steady job.'],
    'hold over': ['We hold the vote over.', 'We held the vote over.', 'We have held the vote over.'],
    'run down': ['The battery runs down quickly.', 'The battery ran down yesterday.', 'The battery has run down again.'],
    'break down': ['My car breaks down occasionally.', 'My car broke down yesterday.', 'My car has broken down twice.'],
    'break up': ['Some couples break up.', 'They broke up last year.', 'They have broken up already.'],
    'set apart': ['The design sets the app apart.', 'The design set the app apart.', 'The design has set the app apart.'],
    'set back': ['The bug sets us back.', 'The bug set us back.', 'The bug has set us back.'],
    'get along with': ['I get along with my colleagues.', 'I got along with my old team.', 'I have always gotten along with them.'],
    'give it a try': ['I give it a try.', 'I gave it a try.', 'I have given it a try.'],
}

GROUP_LABELS = {
'VERBS': 'Частые глаголы', 'PEOPLE':'Люди и общение', 'TIME':'Время и места',
'HOME':'Повседневная жизнь', 'WORK':'Работа и технологии', 'FEELINGS':'Чувства и качества',
'LEARNING':'Учёба и идеи', 'GET':'Фразы с GET', 'TAKE':'Фразы с TAKE',
'LOOK':'Фразы с LOOK', 'GO':'Фразы с GO', 'COME':'Фразы с COME',
'PUT':'Фразы с PUT', 'GIVE':'Фразы с GIVE', 'MAKE':'Фразы с MAKE',
'TURN':'Фразы с TURN', 'BRING':'Фразы с BRING', 'HOLD':'Фразы с HOLD',
'KEEP':'Фразы с KEEP', 'SET':'Фразы с SET', 'RUN':'Фразы с RUN',
'MIXED':'Другие выражения'
}

def parse(filename, kind):
    entries=[]; group=None; counter=0
    for line_number, raw in enumerate((ROOT/'data'/filename).read_text(encoding='utf-8').splitlines(), 1):
        raw=raw.strip()
        if not raw: continue
        if raw.startswith('#'):
            group=raw[1:].split('|',1)[0].strip()
            if group not in GROUP_LABELS: raise ValueError(group)
            counter=0
            continue
        parts=[p.strip() for p in raw.split('|')]
        if len(parts)!=4 or any(not p for p in parts):
            raise ValueError(f'{filename}:{line_number}: expected term|ru|synonyms|example')
        term,ru,syn,example=parts
        if not re.fullmatch(r'[a-zA-Z ]+',term): raise ValueError(f'Invalid term {term}')
        counter+=1
        card={'id':('w' if kind=='word' else 'p')+str(len(entries)+1),
              'en':term,'ru':ru,'syn':syn,'ex':example,'group':group,'kind':kind}
        root=term.lower().split()[0]
        if root in IRREGULAR and (kind=='phrase' or group=='VERBS' or term.lower() in ('build','sleep')):
            past,part=IRREGULAR[root]
            rest=term[len(root):]
            card['forms']=[term,past+rest,part+rest]
            if kind=='word':
                card['examples']=VERB_EXAMPLES[root]
            elif term in PHRASE_OVERRIDES:
                card['examples']=PHRASE_OVERRIDES[term]
            else:
                tail=TAILS[group][counter-1]
                sentences=[]
                for verb,append in ((root,''),(past,' yesterday'),(part,' before')):
                    term2=verb+rest
                    if append==' before':
                        sentences.append('I have '+term2+' '+tail+' before.')
                    else:
                        sentences.append('I '+term2+' '+tail+append+'.')
                card['examples']=sentences
        entries.append(card)
    return entries

words=parse('words.tsv','word')
phrases=parse('phrases.tsv','phrase')
cards=words+phrases
if (len(words),len(phrases),len(cards))!=(350,150,500):
    raise ValueError(f'Expected 350/150/500, got {len(words)}/{len(phrases)}/{len(cards)}')
seen=set()
for item in cards:
    if item['en'].lower() in seen: raise ValueError('duplicate: '+item['en'])
    seen.add(item['en'].lower())
    if item.get('forms') and len(item['examples'])!=3:
        raise ValueError('invalid forms examples: '+item['en'])
    if len(item['ex'])>100: raise ValueError('Example too long: '+item['en'])

groups=[{'id':key,'name':value,'count':sum(x['group']==key for x in cards),
         'type':'phrases' if key not in ['VERBS','PEOPLE','TIME','HOME','WORK','FEELINGS','LEARNING'] else 'words'}
        for key,value in GROUP_LABELS.items()]
# Minimal memory footprint; UTF-8 preserved for correct Russian font rendering.
json_text=json.dumps(cards,ensure_ascii=False,separators=(',',':'))
groups_text=json.dumps(groups,ensure_ascii=False,separators=(',',':'))
(ROOT/'src/common/cards.js').write_text('/* Generated from curated TSV: python3 scripts/generate_data.py */\nexport default '+json_text+'\n',encoding='utf-8')
(ROOT/'src/common/groups.js').write_text('/* Generated from curated TSV */\nexport default '+groups_text+'\n',encoding='utf-8')
(ROOT/'preview/cards.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'preview/groups.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'preview/data.js').write_text('window.LINGO_CARDS = '+json_text+';\nwindow.LINGO_GROUPS = '+groups_text+';\n',encoding='utf-8')
print(f'Generated {len(words)} words and {len(phrases)} expressions in {len(groups)} groups; JS data {len(json_text.encode())/1024:.1f} KiB')
