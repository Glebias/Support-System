'use server'
import database from '@/modules/database'

export default async function selectUsers() {
  const result = await database
    .selectFrom('users')
    .select(['users.email', 'users.password'])
    .execute()
    return result
}
