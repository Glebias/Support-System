'use client'
import { useEffect, useRef, useState } from 'react'
import { Message } from '@/types/chat'
import styles from './ChatSelector.module.css'

interface ChatSelectorProps {
  isOpen: boolean
  onClose: () => void
  messages: Message[]
  onChatSelect: (chatId: number) => void
  selectedChatId?: number
  onCreateNewChat?: (chatName: string) => void
}

export default function ChatSelector({ 
  isOpen, 
  onClose, 
  messages, 
  onChatSelect, 
  selectedChatId,
  onCreateNewChat
}: ChatSelectorProps) {
  const modalRef = useRef<HTMLDivElement>(null)
  const [showNameInput, setShowNameInput] = useState(false)
  const [chatName, setChatName] = useState('')
  const [nameError, setNameError] = useState('')

  const truncateText = (text: string, maxLength: number = 30): string => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength - 3) + '...'
  }

  const truncateLastMessage = (text: string, maxLength: number = 50): string => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength - 3) + '...'
  }

  const getChatsFromMessages = () => {
    const chatMap = new Map<number, {
      id: number
      name: string
      lastMessage?: string
      lastMessageTime: string
      messageCount: number
      hasUnread: boolean
      lastMessageIsAnswer: boolean
    }>()

    messages.forEach(msg => {
      if (msg.chat) {
        const chatId = parseInt(msg.chat)
        
        if (!chatMap.has(chatId)) {
          const chatName = truncateText(msg.text, 30)
          
          chatMap.set(chatId, {
            id: chatId,
            name: chatName,
            lastMessageTime: msg.createdAt,
            messageCount: 0,
            hasUnread: false,
            lastMessageIsAnswer: msg.answer
          })
        }
        
        const chat = chatMap.get(chatId)!
        chat.messageCount++
        
        const parseTime = (timeStr: string) => {
          const [time, date] = timeStr.split(' ')
          const [day, month, year] = date.split('.')
          return new Date(`${year}-${month}-${day}T${time}`).getTime()
        }
        
        const currentTime = parseTime(chat.lastMessageTime)
        const newTime = parseTime(msg.createdAt)
        
        if (newTime >= currentTime) {
          chat.lastMessage = truncateLastMessage(msg.text, 50)
          chat.lastMessageTime = msg.createdAt
          chat.lastMessageIsAnswer = msg.answer
          chat.hasUnread = !msg.answer
        }
      }
    })

    return Array.from(chatMap.values()).sort((a, b) => {
      if (a.hasUnread && !b.hasUnread) return 1
      if (!a.hasUnread && b.hasUnread) return -1
      
      const parseTime = (timeStr: string) => {
        const [time, date] = timeStr.split(' ')
        const [day, month, year] = date.split('.')
        return new Date(`${year}-${month}-${day}T${time}`).getTime()
      }
      
      const timeA = parseTime(a.lastMessageTime)
      const timeB = parseTime(b.lastMessageTime)
      return timeB - timeA
    })
  }

  const chats = getChatsFromMessages()

  const isChatNameUnique = (name: string): boolean => {
    return !chats.some(chat => 
      chat.name.toLowerCase() === name.toLowerCase().trim()
    )
  }

  const handleCreateChatClick = () => {
    setShowNameInput(true)
    setNameError('')
    setChatName('')
  }

  const handleCreateChat = () => {
    if (!onCreateNewChat || !chatName.trim()) return

    const trimmedName = chatName.trim()
    
    if (!isChatNameUnique(trimmedName)) {
      setNameError('Чат с таким названием уже существует')
      return
    }

    if (trimmedName.length > 100) {
      setNameError('Название чата не должно превышать 100 символов')
      return
    }

    onCreateNewChat(trimmedName)
    setShowNameInput(false)
    setChatName('')
    setNameError('')
  }

  const handleCancelCreate = () => {
    setShowNameInput(false)
    setChatName('')
    setNameError('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleCreateChat()
    }
  }

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setChatName(e.target.value)
    if (nameError) {
      setNameError('')
    }
  }

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        if (showNameInput) {
          handleCancelCreate()
        } else {
          onClose()
        }
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose, showNameInput])

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      if (showNameInput) {
        handleCancelCreate()
      } else {
        onClose()
      }
    }
  }

  const handleChatClick = (chatId: number) => {
    onChatSelect(chatId)
  }

  if (!isOpen) return null

  return (
    <section 
      className={isOpen ? styles.modalVisible : styles.modalUnvisible}
      onClick={handleOverlayClick}
      ref={modalRef}
    >
      <div className={styles.modalContent}>
        <div className={styles.formHeader}>
          <h2>Мои чаты</h2>
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
          {showNameInput ? (
            <div className={styles.nameInputSection}>
              <div className={styles.inputGroup}>
                <label htmlFor="chatName" className={styles.inputLabel}>
                  Название чата
                </label>
                <input
                  id="chatName"
                  type="text"
                  className={`${styles.nameInput} ${nameError ? styles.inputError : ''}`}
                  value={chatName}
                  onChange={handleNameChange}
                  onKeyPress={handleKeyPress}
                  placeholder="Введите название чата..."
                  autoFocus
                  maxLength={100}
                />
                {nameError && (
                  <div className={styles.errorText}>{nameError}</div>
                )}
                <div className={styles.inputHint}>
                  Максимум 100 символов
                </div>
              </div>
              
              <div className={styles.nameActions}>
                <button
                  className={styles.cancelButton}
                  onClick={handleCancelCreate}
                >
                  Отменить
                </button>
                <button
                  className={styles.createButton}
                  onClick={handleCreateChat}
                  disabled={!chatName.trim()}
                >
                  Создать чат
                </button>
              </div>
            </div>
          ) : (
            <>
              {onCreateNewChat && (
                <div className={styles.createChatSection}>
                  <button 
                    className={styles.createChatButton}
                    onClick={handleCreateChatClick}
                  >
                    + Создать новый чат
                  </button>
                </div>
              )}
              
              <div className={styles.chatsList}>
                {chats.length === 0 ? (
                  <div className={styles.emptyState}>
                    <p className={styles.emptyText}>У вас пока нет чатов</p>
                    {onCreateNewChat && (
                      <button 
                        className={styles.createFirstChatButton}
                        onClick={handleCreateChatClick}
                      >
                        Создать первый чат
                      </button>
                    )}
                  </div>
                ) : (
                  chats.map((chat) => (
                    <button
                      key={chat.id}
                      className={`${styles.chatItem} ${
                        selectedChatId === chat.id ? styles.chatItemSelected : ''
                      } ${chat.hasUnread ? styles.chatItemUnread : ''} ${
                        chat.lastMessageIsAnswer ? styles.chatItemAnswer : ''
                      }`}
                      onClick={() => handleChatClick(chat.id)}
                    >
                      <div className={styles.chatInfo}>
                        <span className={styles.chatName} title={chat.name}>
                          {chat.name}
                          {chat.hasUnread && <span className={styles.unreadIndicator}> ●</span>}
                        </span>
                        {chat.lastMessage && (
                          <span className={styles.lastMessage} title={chat.lastMessage}>
                            {truncateText(chat.lastMessage, 25)}
                          </span>
                        )}
                        <span className={styles.chatMeta}>
                          Сообщений: {chat.messageCount} • {chat.lastMessageTime}
                        </span>
                      </div>
                      {selectedChatId === chat.id && (
                        <div className={styles.selectedIndicator}>✓</div>
                      )}
                      {chat.lastMessageIsAnswer && !chat.hasUnread && (
                        <div className={styles.answerIndicator}>✓</div>
                      )}
                    </button>
                  ))
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  )
}