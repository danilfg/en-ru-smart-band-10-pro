const test = require('node:test')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const root=path.resolve(__dirname,'..')
const readJs = name => {
  const s=fs.readFileSync(path.join(root,'src/common',name),'utf8')
  return JSON.parse(s.slice(s.indexOf('export default ')+15).trim())
}
const cards=readJs('cards.js')
const groups=readJs('groups.js')
test('exactly 350 standalone words and 150 expressions',()=>{
  assert.equal(cards.length,500)
  assert.equal(cards.filter(c=>c.kind==='word').length,350)
  assert.equal(cards.filter(c=>c.kind==='phrase').length,150)
  assert.equal(new Set(cards.map(c=>c.en.toLowerCase())).size,500)
  assert.equal(new Set(cards.map(c=>c.id)).size,500)
})
test('22 learner-friendly groups, all cards accounted for',()=>{
  assert.equal(groups.length,22)
  assert.equal(groups.reduce((n,g)=>n+g.count,0),500)
  for (const g of groups) assert.equal(cards.filter(c=>c.group===g.id).length,g.count)
  assert.equal(groups.filter(g=>g.type==='phrases').length,15)
  assert.equal(groups.find(g=>g.id==='GET').count,10)
  assert.equal(groups.find(g=>g.id==='HOLD').count,10)
})
test('every card is translated and has synonyms and an English usage example',()=>{
  for (const c of cards) {
    assert.ok(c.en.length && c.ru.length && c.syn.length && c.ex.length,c.id)
    assert.match(c.ru,/[а-яё]/i,c.en)
    assert.ok(c.ex.endsWith('.') || c.ex.endsWith('!') || c.ex.endsWith('?'),c.en)
    assert.ok(c.ex.length<=100,c.en)
  }
})
test('all marked irregular verbs show V1/V2/V3 and three examples',()=>{
  const irregular=cards.filter(c=>c.forms)
  assert.ok(irregular.length>=120,'Expected phrasal-verb coverage')
  for (const c of irregular) {
    assert.equal(c.forms.length,3,c.en)
    assert.equal(c.examples.length,3,c.en)
    for (const e of c.examples) assert.ok(e.trim().endsWith('.'),c.en)
  }
  assert.deepEqual(cards.find(c=>c.en==='go').forms,['go','went','gone'])
  assert.deepEqual(cards.find(c=>c.en==='hold').forms,['hold','held','held'])
  assert.deepEqual(cards.find(c=>c.en==='get up').forms,['get up','got up','gotten up'])
})
test('source dataset clean and generated files reproducible',()=>{
  assert.ok(fs.statSync(path.join(root,'src/common/cards.js')).size < 140*1024)
  const c=cards.find(c=>c.en==='get over'); assert.equal(c.ru,'оправиться; преодолеть')
})
