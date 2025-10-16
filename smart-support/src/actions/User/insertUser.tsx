'use server'
import database from '@/modules/database'
import jwt from '@/sorse/jwt'
import { hash } from '@node-rs/bcrypt'
import { cookies } from 'next/headers'

interface User {
  email: string
  password: string
}

export default async function insertUser(user: User) {
  const registration = await database
    .insertInto('users')
    .values({
      email: user.email,
      password: await hash(user.password),
      role: 'user'
    })
    .returning(['id', 'role'])
    .executeTakeFirst()
    if (registration){
      const token = await jwt({id: registration.id, role: registration.role})
      const cookieStore = await cookies()
      const expiresAt = new Date(Date.now() + 2 * 24 * 60 * 60 * 1000)
      cookieStore.set('session', token, {
        expires: expiresAt,
    httpOnly: true,
    path: '/',
    sameSite: 'lax'
  })
    }
}
