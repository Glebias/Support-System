'use server'
import database from '@/modules/database'

interface UserMessage{
        user_id: number,
        text: string,
        chat: string
}

export default async function insertAnswerAdmin(user:UserMessage) {
    database
      .insertInto('messages')
      .values({
        user: user.user_id,
        text: user.text,
        active: false,
        answer: true,
        chat: user.chat
      })
      .executeTakeFirst()

    database
      .updateTable('messages')
      .set({ active: false })
      .where('chat', '=', user.chat)
      .where('user', '=', user.user_id)
      .where('active', '=', true)
      .execute()
}