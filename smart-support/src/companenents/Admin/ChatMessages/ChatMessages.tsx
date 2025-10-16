'use client'
import { useEffect, useRef } from 'react'
import Message, { MessageProps } from '@/companenents/Admin/Message/Message'
import styles from './ChatMessages.module.css'

interface ChatMessagesProps {
  messages: MessageProps[]
}

export default function ChatMessages({ messages }: ChatMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  return (
    <div className={styles.chatMessages}>
      {messages?.map((message, index) => (
        <Message key={index} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  )
}