const test = require('node:test')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const vm = require('node:vm')
const root = path.resolve(__dirname, '..')
const parseModule = name => {
  const str = fs.readFileSync(path.join(root,'src/common',name),'utf8')
  return JSON.parse(str.slice(str.indexOf('export default ')+15))
}
const cards=parseModule('cards.js'), groups=parseModule('groups.js')
const ux=fs.readFileSync(path.join(root,'src/pages/index/index.ux'),'utf8')
const text=ux.match(/<script>([\s\S]*?)<\/script>/)[1]
  .replace(/^import .*?\n/gm,'').replace('export default {','module.exports = {')
function create(storageMap) {
  const closed = {value:false}
  const storage = {
    get:({key,success,fail})=>storageMap.has(key)?success({data:storageMap.get(key)}):fail(),
    set:({key,value,success})=>{storageMap.set(key,value); success?.()}
  }
  const module={exports:{}}
  vm.runInNewContext(text,{module,storage,app:{terminate:()=>closed.value=true},cards,groups,Date,Math,JSON,console})
  const def=module.exports
  const instance=Object.assign({},def.private,def)
  instance.onInit()
  return {instance,closed,storageMap}
}
test('watch can open a group, flip, grade and persist progress between launches',()=>{
  const store=new Map([['lingoinview_wear_reviews_v1','{}']])
  const first=create(store).instance
  assert.equal(first.mode,'home')
  first.openGroups()
  assert.equal(first.mode,'groups')
  first.chooseGroup('VERBS')
  assert.equal(first.mode,'card')
  assert.equal(first.currentWord,'be')
  assert.equal(first.positionLabel,'1 / 60')
  first.flipCard();assert.equal(first.flipped,true)
  first.answerYes();assert.equal(first.currentWord,'have')
  first.answerNo();assert.equal(first.currentWord,'do')
  assert.equal(first._progress.w1.level,1)
  assert.equal(first._progress.w2.level,0)
  assert.ok(first._progress.w1.due>Date.now())
  assert.equal(first.sessionKnown,1);assert.equal(first.sessionWrong,1)
  assert.ok(store.get('lingoinview_wear_reviews_v1').includes('"w1"'))
  first.goHome();assert.equal(first.studiedCount,2)
  const second=create(store).instance
  assert.equal(second.studiedCount,2)
  assert.equal(second.masteredCount,1)
  second.openGroups();assert.ok(second.visibleGroups[0].progress.includes('2 / 60'))
})
test('dedicated exit and watch back gesture do not unpair or reset the device',()=>{
  const store=new Map([['lingoinview_wear_reviews_v1','{}']])
  const obj=create(store), w=obj.instance
  w.openGroups();w.chooseGroup('HOLD');w.onBackPress()
  assert.equal(w.mode,'groups')
  w.onBackPress();assert.equal(w.mode,'home')
  w.onBackPress();assert.equal(obj.closed.value,true)
  assert.equal(typeof w._progress,'object')
})
test('due review queue prioritizes failed cards over unreviewed words',()=>{
  const store=new Map([['lingoinview_wear_reviews_v1','{}']])
  const w=create(store).instance
  w.chooseGroup('GET');w.answerNo();
  // Mark this failed card as due now to test the due queue.
  w._progress.p1.due=Date.now()-1
  w.startReview()
  assert.equal(w.mode,'card')
  assert.equal(w.currentWord,'get up')
  assert.equal(w._queue.length,21)
})
