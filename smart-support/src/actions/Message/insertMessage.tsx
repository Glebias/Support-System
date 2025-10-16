'use server'
import database from '@/modules/database'

interface Message {
  id: number
  user?: number
  text: string
  active: boolean
  createdAt: Date
  answer: boolean
  chat?: string
}

export default async function insertUser(message: Message) {
  if(message.chat && message.user){
    database
      .insertInto('messages')
      .values({
        user: message.user,
        text: message.text,
        active: message.active,
        answer: message.answer,
        chat: message.chat
      })
      .executeTakeFirst()
  }
  else {
    database
      .insertInto('messages')
      .values({
        text: message.text,
        active: message.active,
        answer: message.answer
      })
      .executeTakeFirst()
  }
}
