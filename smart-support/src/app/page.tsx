'use client'
import { useEffect, useState, useRef } from "react";
import styles from "./page.module.css";
import Header from "@/companenents/Header/Header";
import Registration from "@/companenents/Registration/Registration";
import Auntification from "@/companenents/Auntification/Auntification";
import ChatSelector from '@/companenents/ChatSelector/ChatSelector'
import { Message } from '@/types/chat'
import Chat from "@/companenents/Chat/Chat";
import loadUserChats from "@/actions/Message/loadUserChats";
import insertMessage from "@/actions/Message/insertMessage";

export default function Page() {
  const [registration, setRegistration] = useState<number>(0)
  const [userId, setUserId] = useState<number | undefined>()
  const [messages, setMessages] = useState<Message[]>([])
  const [currentChatId, setCurrentChatId] = useState<number | undefined>()
  const [isChatSelectorOpen, setIsChatSelectorOpen] = useState(false)
  const [accentColor, setAccentColor] = useState('#059669')
  const [textColor, setTextColor] = useState('#1F2937')
  const [isInputDisabled, setIsInputDisabled] = useState(false)
  const [newChatName, setNewChatName] = useState<string>('')
  
  const lastMessageTimeRef = useRef<number>(Date.now())
  const refreshIntervalRef = useRef<NodeJS.Timeout>()

  const getCurrentTime = (): string => {
    const now = new Date();
    return now.toLocaleTimeString('ru-RU', { 
      hour: '2-digit', 
      minute: '2-digit'
    }) + ' ' + now.toLocaleDateString('ru-RU');
  };

  const checkIfInputShouldBeEnabled = (chatMessages: Message[]) => {
    if (chatMessages.length === 0) {
      setIsInputDisabled(false);
      return;
    }
    
    const lastMessage = chatMessages[chatMessages.length - 1];
    
    if (lastMessage.answer) {
      setIsInputDisabled(false);
    } else {
      setIsInputDisabled(true);
    }
  };

  const createTemporaryChat = (): Message[] => {
    const tempMessages: Message[] = [
      {
        id: 1,
        text: "Добро пожаловать! Вы можете начать общение без регистрации, но оставьте свой адрес электронной почты в сообщении.",
        active: true,
        answer: true,
        createdAt: getCurrentTime()
      }
    ]
    return tempMessages
  }

  const findMostRecentChat = (messages: Message[]): number | undefined => {
    if (messages.length === 0) return undefined
    
    const chatLastActivity = new Map<number, { time: number, hasUnread: boolean }>()
    
    messages.forEach(msg => {
      if (msg.chat) {
        const chatId = parseInt(msg.chat)
        const [time, date] = msg.createdAt.split(' ')
        const [day, month, year] = date.split('.')
        const messageTime = new Date(`${year}-${month}-${day}T${time}`).getTime()
        
        if (!chatLastActivity.has(chatId) || messageTime > chatLastActivity.get(chatId)!.time) {
          const isUnread = !msg.answer
          chatLastActivity.set(chatId, { 
            time: messageTime, 
            hasUnread: isUnread 
          })
        }
      }
    })
    
    const sortedChats = Array.from(chatLastActivity.entries())
      .sort(([chatIdA, dataA], [chatIdB, dataB]) => {
        if (dataA.hasUnread && !dataB.hasUnread) return 1
        if (!dataA.hasUnread && dataB.hasUnread) return -1
        return dataB.time - dataA.time
      })
    
    return sortedChats.length > 0 ? sortedChats[0][0] : undefined
  }

  const loadMessages = async () => {
    try {
      if (userId) {
        const userMessages = await loadUserChats(userId)
        setMessages(userMessages)
        
        if (userMessages.length > 0) {
          const recentChat = findMostRecentChat(userMessages)
          setCurrentChatId(recentChat)
          const chatMessages = userMessages.filter(msg => msg.chat === recentChat?.toString())
          checkIfInputShouldBeEnabled(chatMessages)
        } else {
          setCurrentChatId(undefined)
          setIsInputDisabled(false)
        }
      } else {
        const tempMessages = createTemporaryChat()
        setMessages(tempMessages)
        setCurrentChatId(undefined)
        checkIfInputShouldBeEnabled(tempMessages)
      }
    } catch (error) {
      console.log('Ошибка загрузки сообщений:', error)
      const tempMessages = createTemporaryChat()
      setMessages(tempMessages)
      setCurrentChatId(undefined)
      checkIfInputShouldBeEnabled(tempMessages)
    }
  }

  const startAutoRefresh = () => {
    refreshIntervalRef.current = setInterval(() => {
      const now = Date.now()
      if (now - lastMessageTimeRef.current >= 10 * 60 * 1000) {
        loadMessages()
      }
    }, 10 * 60 * 1000)
  }
  useEffect(() => {
    loadMessages()
    startAutoRefresh()
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current)
      }
    }
  }, [userId])

  const getCurrentChatMessages = (): Message[] => {
    if (!userId) {
      return messages.filter(msg => !msg.chat)
    }
    
    if (!currentChatId) return []
    return messages.filter(msg => msg.chat === currentChatId.toString())
  }

  const handleCreateNewChat = async (chatName: string) => {
    if (!userId) return
    
    const newChatId = Date.now()
    
    setNewChatName(chatName)
    
    setCurrentChatId(newChatId)
    setIsChatSelectorOpen(false)
    
    setMessages(prev => prev.filter(msg => msg.chat !== newChatId.toString()))
    
    setIsInputDisabled(false)
  }

  const handleSendMessage = async (text: string) => {
    
    setIsInputDisabled(true)
    lastMessageTimeRef.current = Date.now()
    
    const newMessage: Message = {
      id: Date.now(),
      text: text,
      active: true,
      answer: false,
      createdAt: getCurrentTime()
    }
    
    if (userId) {
      newMessage.user = userId
    }
    
    if (currentChatId) {
      newMessage.chat = currentChatId.toString()
    }
    
    try {
      insertMessage(newMessage)
      setMessages(prev => [...prev, newMessage])
      
      if (newChatName) {
        setNewChatName('')
      }
      
    } catch (error) {
      console.log('Ошибка отправки сообщения:', error)
    }
  }

  const handleChatSelect = (chatId: number) => {
    setCurrentChatId(chatId)
    setIsChatSelectorOpen(false)
    const chatMessages = messages.filter(msg => msg.chat === chatId.toString())
    checkIfInputShouldBeEnabled(chatMessages)
    
    setNewChatName('')
  }

  const handleOpenChatSelector = () => {
    if (!userId) {
      setRegistration(1)
      return
    }
    setIsChatSelectorOpen(true)
  }
  return (
    <>
      <Header 
        setUserId={setUserId} 
        registration={registration} 
        setRegistration={setRegistration} 
        onChatButtonClick={handleOpenChatSelector} 
        accentColor={accentColor} 
        setTextColor={setTextColor}
        setAccentColor={setAccentColor} 
      />
      
      <main className={styles.main}>
        {!userId && (
          <Chat 
            key="temporary-chat"
            messages={getCurrentChatMessages()}
            onSendMessage={handleSendMessage}
            accentColor={accentColor}
            isInputDisabled={isInputDisabled}
          />
        )}
        
        {userId && currentChatId && (
          <Chat 
            key={currentChatId}
            messages={getCurrentChatMessages()}
            onSendMessage={handleSendMessage}
            textColor={textColor}
            accentColor={accentColor}
            isInputDisabled={isInputDisabled}
            initialMessage={newChatName}
          />
        )}
        
        {userId && !currentChatId && messages.length === 0 && (
          <div className={styles.welcome}>
            <p>У вас пока нет чатов</p>
            <button 
              className={styles.createFirstChatButton}
              onClick={() => setIsChatSelectorOpen(true)}
            >
              Создать первый чат
            </button>
          </div>
        )}
        
        {registration === 1 && (
          <Registration registration={registration} setRegistration={setRegistration} />
        )}
        {registration === 2 && (
          <Auntification registration={registration} setRegistration={setRegistration} />
        )}
      </main>

      {userId && (
        <ChatSelector
          isOpen={isChatSelectorOpen}
          onClose={() => setIsChatSelectorOpen(false)}
          messages={messages}
          onChatSelect={handleChatSelect}
          selectedChatId={currentChatId}
          onCreateNewChat={handleCreateNewChat}
        />
      )}
    </>
  );
}