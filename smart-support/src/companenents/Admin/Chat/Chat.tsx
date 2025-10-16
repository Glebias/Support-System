'use client'
import { useEffect, useState } from 'react'
import ChatMessages from '@/companenents/Admin/ChatMessages/ChatMessages'
import ChatInput from './ChatInput/ChatInput'
import AnalysisPanel from '@/companenents/Admin/AnalysisPanel/AnalysisPanel'
import { Message } from '@/types/chat'
import styles from './Chat.module.css'
import { number } from 'valibot'

interface ChatProps {
  textColor: string
  messages: Message[]
  onSendMessage: (text: string) => void
  onNextChat: () => void
  accentColor: string
  isInputDisabled: boolean
  currentChat: Message | null
}

export default function Chat({
  textColor, 
  messages, 
  onSendMessage, 
  onNextChat, 
  accentColor, 
  isInputDisabled, 
  currentChat 
}: ChatProps) {
  const [displayMessages, setDisplayMessages] = useState<Message[]>([]);

  useEffect(() => {
    setDisplayMessages(messages)
  }, [messages])

  const handleSendMessage = (text: string) => {
    onSendMessage(text)
  };

const handleRunAnalysis = async (): Promise<string> => {
  // return {score: 0.9999997615814209, offered_responce: 'Мобильное приложение VTB mBank можно скачать в App…тернет-банка и пройдите первоначальную настройку.', main_category: 'Новые клиенты', sub_category: 'Первые шаги'}
  try {
    const response = await fetch('http://localhost:8000/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        question: displayMessages[0].text
      }),
    });
    console.log(response)
    if (!response.ok) {
      throw new Error('Ошибка анализа')
    }
    
    const data = await response.json()
    
    if (data.offered_responce && typeof data.offered_responce === 'string') {
      return {score: data.score, offered_responce: data.offered_responce, main_category: data.main_category, sub_category: data.sub_category};
    } else {
      throw new Error('Некорректный формат ответа от сервера')
    }
    
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Произошла ошибка при анализе')
  }
};

  return (
    <div className={styles.chatContainer}>
      <div className={styles.mainContent}>
        <div className={styles.chatSection}>
          <ChatMessages messages={displayMessages} />
        </div>
        <AnalysisPanel
          accentColor={accentColor}
          onRunAnalysis={handleRunAnalysis}
          isAnalysisDisabled={displayMessages.length === 0}
          initialExpanded={true}
        />
      </div>
      
      <ChatInput 
        messages={displayMessages}
        onSendMessage={handleSendMessage}
        onNextChat={onNextChat}
        accentColor={accentColor}
        textColor={textColor}
        disabled={isInputDisabled}
        hasUserId={!!currentChat?.user}
      />
    </div>
  );
}