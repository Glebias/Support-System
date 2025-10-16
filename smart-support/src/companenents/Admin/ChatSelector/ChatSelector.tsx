'use client'
import { useEffect, useRef } from 'react'
import styles from './ChatSelector.module.css'

interface Chat {
  id: number
  name: string
  hasUser: boolean
}

interface ChatSelectorProps {
  isOpen: boolean
  onClose: () => void
  chats: Chat[]
  onChatSelect: (chatId: number) => void
  selectedChatId?: number
}

export default function ChatSelector({ 
  isOpen, 
  onClose, 
  chats, 
  onChatSelect, 
  selectedChatId
}: ChatSelectorProps) {
  const modalRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  const handleChatClick = (chatId: number) => {
    onChatSelect(chatId)
  }

  if (!isOpen) return null

const truncateText = (text: string, maxLength: number = 30): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength - 3) + '...'
}
  return (
    <section 
      className={isOpen ? styles.modalVisible : styles.modalUnvisible}
      onClick={handleOverlayClick}
      ref={modalRef}
    >
      <div className={styles.modalContent}>
        <div className={styles.formHeader}>
          <h2>Чаты для ответа</h2>
          <button 
            type="button" 
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Закрыть выбор чата"
          >
            ×
          </button>
        </div>

        <div className={styles.chatsContainer}>
          {chats.length === 0 ? (
            <div className={styles.emptyState}>
              <p className={styles.emptyText}>Нет чатов для ответа</p>
            </div>
          ) : (
            <div className={styles.chatsList}>
              {chats.map((chat) => (
                <button
                  key={chat.id}
                  className={`${styles.chatItem} ${
                    selectedChatId === chat.id ? styles.chatItemSelected : ''
                  } ${!chat.hasUser ? styles.chatItemNoUser : ''}`}
                  onClick={() => handleChatClick(chat.id)}
                >
                  <div className={styles.chatInfo}>
                    <span className={styles.chatName}>
                      {truncateText(chat.name, 25)}
                      {!chat.hasUser && <span className={styles.noUserIndicator}> (нет user_id)</span>}
                    </span>
                    <span className={styles.chatMeta}>
                      {chat.hasUser ? 'Можно ответить' : 'Только просмотр'}
                    </span>
                  </div>
                  {selectedChatId === chat.id && (
                    <div className={styles.selectedIndicator}>✓</div>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}