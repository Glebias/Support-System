import { CamelCasePlugin, type GeneratedAlways, Kysely, PostgresDialect } from 'kysely'
import { Pool } from 'pg'


export interface UserTable {
  id: GeneratedAlways<number>
  email: string
  password: string
  createdAt: GeneratedAlways<Date>
  role: string
}

export interface MessageTable {
  id: GeneratedAlways<number>
  createdAt: GeneratedAlways<Date>
  user?: number
  text: string 
  active: boolean
  answer: boolean
  chat?: string
}

export interface Database {
  users: UserTable
  messages: MessageTable
}

const database = new Kysely<Database>({
  dialect: new PostgresDialect({
    pool: new Pool({
      connectionString: process.env.DATABASE_CONNECTION_STRING
    })
  }),
  plugins: [
    new CamelCasePlugin({
      maintainNestedObjectKeys: true
    })
  ]
})

export default database
