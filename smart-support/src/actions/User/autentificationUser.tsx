'use server'
import database from '@/modules/database'
import jwt from '@/sorse/jwt'
import { hash, verify } from '@node-rs/bcrypt'
import { cookies } from 'next/headers'

interface User {
  email: string
  password: string
}

export default async function autentificationUser(user: User) {
  const registration = await database
    .selectFrom('users')
    .select([
      'users.id',
      'users.email',
      'users.password',
      'users.role'
    ])
    .where('users.email', '=', user.email)
    .execute()
    if(!await verify(user.password, registration[0].password)){
      return false
    }
    if (registration){
      const token = await jwt({id: registration[0].id, role: registration[0].role})
      const cookieStore = await cookies()
      const expiresAt = new Date(Date.now() + 2 * 24 * 60 * 60 * 1000)
      cookieStore.set('session', token, {
        expires: expiresAt,
    httpOnly: true,
    path: '/',
    sameSite: 'lax'
  })
    }
    return true
}
