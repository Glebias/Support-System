'use client'
import { useState, useRef, useEffect } from 'react'
import styles from './ChatInput.module.css'
import updateAnnonimQuestions from '@/actions/Message/Admin/updateAnnonimQuestions'
import { Message } from '@/types/chat'

interface ChatInputProps {
  messages: Message[]
  textColor: string
  onSendMessage: (text: string) => void
  onNextChat: () => void
  accentColor: string
  disabled?: boolean
  hasUserId: boolean
}

export default function ChatInput({ 
  messages,
  textColor, 
  onSendMessage, 
  onNextChat, 
  accentColor, 
  disabled = false,
  hasUserId 
}: ChatInputProps) {
  const [inputText, setInputText] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const baseHeightRef = useRef<number>(0)

  // Инициализация базовой высоты
  useEffect(() => {
    if (textareaRef.current) {
      const computedStyle = window.getComputedStyle(textareaRef.current)
      const lineHeight = parseInt(computedStyle.lineHeight) || 20
      const padding = parseInt(computedStyle.paddingTop) + parseInt(computedStyle.paddingBottom)
      baseHeightRef.current = lineHeight + padding
    }
  }, [])

  // Автоматическое изменение высоты
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current
    if (!textarea) return

    textarea.style.height = 'auto'
    
    const baseHeight = baseHeightRef.current || 40
    const maxHeight = baseHeight * 3
    
    const scrollHeight = textarea.scrollHeight
    const newHeight = Math.min(scrollHeight, maxHeight)
    
    textarea.style.height = `${newHeight}px`
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value)
    adjustTextareaHeight()
  }

  const handleSendMessage = () => {
    if (inputText.trim() && !disabled && hasUserId) {
      onSendMessage(inputText.trim())
      setInputText('')
      // Сбрасываем высоту после отправки
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.style.height = 'auto'
        }
      }, 0)
    }
  }

  const handleNextChat = () => {
    if (!hasUserId) {
      updateAnnonimQuestions(messages[0].id)
      onNextChat();
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (hasUserId) {
        handleSendMessage();
      }
    }
  }

  return (
    <div className={styles.chatInputContainer}>
      <div className={styles.inputWrapper}>
        <textarea
          ref={textareaRef}
          className={styles.chatInput}
          value={inputText}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder={
            !hasUserId ? "Анонимный пользователь" :
            disabled ? "Отправка..." : "Введите ответ..."
          }
          rows={1}
          disabled={disabled || !hasUserId}
          style={{
            resize: 'none',
            overflowY: 'auto'
          }}
        />
      </div>

      {hasUserId ? (
        <button
          className={styles.sendButton}
          onClick={handleSendMessage}
          disabled={!inputText.trim() || disabled}
          style={{ 
            backgroundColor: disabled ? 'var(--border)' : accentColor,
            cursor: disabled ? 'not-allowed' : 'pointer'
          }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill={textColor} viewBox="0 0 256 256">
            <path d="M227.32,28.68a16,16,0,0,0-15.66-4.08l-.15,0L19.57,82.84a16,16,0,0,0-2.49,29.8L102,154l41.3,84.87A15.86,15.86,0,0,0,157.74,248q.69,0,1.38-.06a15.88,15.88,0,0,0,14-11.51l58.2-191.94c0-.05,0-.1,0-.15A16,16,0,0,0,227.32,28.68ZM157.83,231.85l-.05.14,0-.07-40.06-82.3,48-48a8,8,0,0,0-11.31-11.31l-48,48L24.08,98.25l-.07,0,.14,0L216,40Z"></path>
          </svg>
        </button>
      ) : (
        <button
          className={styles.nextButton}
          onClick={handleNextChat}
          style={{ 
            backgroundColor: accentColor,
          }}
        >
          Следующий
        </button>
      )}
    </div>
  );
}