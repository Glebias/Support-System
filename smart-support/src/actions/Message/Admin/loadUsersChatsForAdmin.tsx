'use server'
import database from '@/modules/database'

export default async function loadUsersChatsForAdmin() {
  const result = await database
    .selectFrom('messages')
    .selectAll()
    .where('messages.active', '=', true)
    .execute()
return result?.map((element) => {
  const date = new Date(element.createdAt)
  const time = date.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
  const chat:string = element.chat || '123412'
  const dateStr = date.toLocaleDateString('ru-RU')
  return {
    ...element,
    chat: chat,
    createdAt: `${time} ${dateStr}`
  }
})
}
