'use server'
import database from '@/modules/database'

export default async function updateAnnonimQuestions(id:number) {

    database
      .updateTable('messages')
      .set({ active: false })
      .where('messages.id', '=', id)
      .execute()
}