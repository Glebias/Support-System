// types/chat.ts
export interface ChatType {
  id: number
  name: string
  createdAt: string
}

export interface ChatHistory {
  chatId: string
  messages: Message[]
}

export interface Message {
  id: number
  user: number
  text: string
  active: boolean
  createdAt: string
  answer: boolean
  chat: string
}

export interface MessageAdmin {
  id: number
  user?: number
  text: string
  active: boolean
  createdAt: string
  answer: boolean
  chat?: string
}