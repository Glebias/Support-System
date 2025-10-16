'use server'
import database from '@/modules/database'

export default async function selectUsersEmail() {
  const result = await database
    .selectFrom('users')
    .select('users.email')
    .execute()
    return result.map(element => element.email)
}
