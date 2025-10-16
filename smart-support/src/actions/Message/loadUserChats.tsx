'use server'
import database from '@/modules/database'

export default async function loadUserChats(id: number) {
  const result = await database
    .selectFrom('messages')
    .selectAll('messages')
    .where('messages.user', '=', id)
    .orderBy('messages.createdAt asc')
    .execute()
return result?.map((element) => {
  const date = new Date(element.createdAt)
  const time = date.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
  const dateStr = date.toLocaleDateString('ru-RU')
  return {
    ...element,
    createdAt: `${time} ${dateStr}`
  }
})
}
