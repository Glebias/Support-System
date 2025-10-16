'use client'
import styles from './Message.module.css'
import { MessageAdmin } from '@/types/chat'

interface MessageProps {
  message: MessageAdmin
}

export default function Message({ message }: MessageProps) {
  return (
    <div
      className={`${styles.message} ${
        message.answer ? styles.messageOther : styles.messageOwn
      }`}
    >
      {message.text && (
        <p className={styles.messageText}>{message.text}</p>
      )}
      
      <div className={styles.messageTime}>
        {message.createdAt}
      </div>
    </div>
  )
}