'use client'
import { useEffect, useState, useRef } from "react";
import styles from "./page.module.css";
import Header from "@/companenents/Header/Header";
import ChatSelector from '@/companenents/Admin/ChatSelector/ChatSelector'
import { Message, MessageAdmin } from '@/types/chat'
import Chat from "@/companenents/Admin/Chat/Chat";
import loadUsersChatsForAdmin from "@/actions/Message/Admin/loadUsersChatsForAdmin";
import insertAnswerAdmin from "@/actions/Message/Admin/insertAnswerAdmin";
import Registration from "@/companenents/Registration/Registration";
import Auntification from "@/companenents/Auntification/Auntification";

export default function AdminPage() {
    const [registration, setRegistration] = useState<number>(0)
  const [userId, setUserId] = useState<number | undefined>()
  const [messages, setMessages] = useState<MessageAdmin[]>([])
  const [currentChatId, setCurrentChatId] = useState<number | undefined>()
  const [isChatSelectorOpen, setIsChatSelectorOpen] = useState(false)
  const [accentColor, setAccentColor] = useState('#059669')
  const [textColor, setTextColor] = useState('#1F2937')
  const [isInputDisabled, setIsInputDisabled] = useState(false)
  
  const lastMessageTimeRef = useRef<number>(Date.now())
  const refreshIntervalRef = useRef<NodeJS.Timeout>()

  const getCurrentTime = (): string => {
    const now = new Date();
    return now.toLocaleTimeString('ru-RU', { 
      hour: '2-digit', 
      minute: '2-digit'
    }) + ' ' + now.toLocaleDateString('ru-RU');
  };

  const getCurrentChat = () => {
    if (!currentChatId) return null;
    const chatMessages = messages.filter(msg => msg.chat === currentChatId.toString());
    return chatMessages.length > 0 ? chatMessages[chatMessages.length - 1] : null;
  };

  const checkIfInputShouldBeEnabled = (chatMessages: Message[]) => {
    if (chatMessages.length === 0) {
      setIsInputDisabled(false);
      return;
    }
    
    const lastMessage = chatMessages[chatMessages.length - 1];
    
    if (lastMessage.user) {
      setIsInputDisabled(false);
    } else {
      setIsInputDisabled(true);
    }
  };

  const getAdminChats = (messages: Message[]) => {
    const chatMap = new Map<number, { time: number, hasUser: boolean }>();
    
    messages.forEach(msg => {
      if (msg.chat) {
        const chatId = parseInt(msg.chat);
        const [time, date] = msg.createdAt.split(' ');
        const [day, month, year] = date.split('.');
        const messageTime = new Date(`${year}-${month}-${day}T${time}`).getTime();
        
        if (!chatMap.has(chatId) || messageTime < chatMap.get(chatId)!.time) {
          const hasUser = !!msg.user;
          chatMap.set(chatId, { 
            time: messageTime, 
            hasUser: hasUser 
          });
        }
      }
    });
    
    return Array.from(chatMap.entries())
      .sort(([chatIdA, dataA], [chatIdB, dataB]) => dataA.time - dataB.time);
  };

  const findFirstChat = (messages: Message[]): number | undefined => {
    const sortedChats = getAdminChats(messages);
    return sortedChats.length > 0 ? sortedChats[0][0] : undefined;
  };

  const loadMessages = async () => {
    try {
      const adminMessages = await loadUsersChatsForAdmin();
      setMessages(adminMessages);
      
      if (adminMessages.length > 0) {
        const firstChat = findFirstChat(adminMessages);
        setCurrentChatId(firstChat);
        if (firstChat) {
          const chatMessages = adminMessages.filter(msg => msg.chat === firstChat.toString());
          checkIfInputShouldBeEnabled(chatMessages);
        }
      } else {
        setCurrentChatId(undefined);
        setIsInputDisabled(true);
      }
    } catch (error) {
      console.log('Ошибка загрузки сообщений:', error);
      setMessages([]);
      setCurrentChatId(undefined);
      setIsInputDisabled(true);
    }
  };

  const startAutoRefresh = () => {
    refreshIntervalRef.current = setInterval(() => {
      const now = Date.now();
      if (now - lastMessageTimeRef.current >= 10 * 60 * 1000) {
        loadMessages();
      }
    }, 10 * 60 * 1000);
  };

  useEffect(() => {
    loadMessages();
    startAutoRefresh();
    
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [userId]);

  const getCurrentChatMessages = (): Message[] => {
    if (!currentChatId) return [];
    return messages.filter(msg => msg.chat === currentChatId.toString());
  };

  const handleSendMessage = async (text: string) => {
    if (!currentChatId) return;
    
    const currentChat = getCurrentChat();
    if (!currentChat?.user) return;
    
    setIsInputDisabled(true);
    lastMessageTimeRef.current = Date.now();
    
    try {
      console.log(currentChatId.toString())
      insertAnswerAdmin({
        user_id: currentChat.user,
        text: text,
        chat: currentChatId.toString()
      });
      
      setMessages(prev => prev.filter(msg => msg.chat !== currentChatId.toString()));
      
      const nextChat = findFirstChat(messages.filter(msg => msg.chat !== currentChatId.toString()));
      setCurrentChatId(nextChat);
      
      if (nextChat) {
        const chatMessages = messages.filter(msg => msg.chat === nextChat.toString());
        checkIfInputShouldBeEnabled(chatMessages);
      }
      
    } catch (error) {
      console.log('Ошибка отправки ответа:', error);
      setIsInputDisabled(false);
    }
  };

  const handleNextChat = () => {
    if (!currentChatId) return;
    
    setMessages(prev => prev.filter(msg => msg.chat !== currentChatId.toString()));
    
    const nextChat = findFirstChat(messages.filter(msg => msg.chat !== currentChatId.toString()));
    setCurrentChatId(nextChat);
    
    if (nextChat) {
      const chatMessages = messages.filter(msg => msg.chat === nextChat.toString());
      checkIfInputShouldBeEnabled(chatMessages);
    }
  };

  const handleChatSelect = (chatId: number) => {
    setCurrentChatId(chatId);
    setIsChatSelectorOpen(false);
    const chatMessages = messages.filter(msg => msg.chat === chatId.toString());
    checkIfInputShouldBeEnabled(chatMessages);
  };

  const handleOpenChatSelector = () => {
    setIsChatSelectorOpen(true);
  };

  const getChatsForSelector = () => {
    return getAdminChats(messages).map(([chatId, data]) => ({
      id: chatId,
      name: `Чат ${chatId}`,
      hasUser: data.hasUser
    }));
  };

  return (
    <>
      <Header 
        setUserId={setUserId} 
        onChatButtonClick={handleOpenChatSelector} 
        accentColor={accentColor} 
        setTextColor={setTextColor}
        setAccentColor={setAccentColor}
        registration={registration} 
        setRegistration={setRegistration}  
      />
      
      <main className={styles.main}>
        {currentChatId && (
          <Chat 
            key={currentChatId}
            messages={getCurrentChatMessages()}
            onSendMessage={handleSendMessage}
            onNextChat={handleNextChat}
            textColor={textColor}
            accentColor={accentColor}
            isInputDisabled={isInputDisabled}
            currentChat={getCurrentChat()}
          />
        )}
        
        {(!currentChatId || messages.length === 0) && (
          <div className={styles.welcome}>
            <p>Все запросы отправлены</p>
            <button 
              className={styles.refreshButton}
              onClick={loadMessages}
            >
              Обновить
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

      <ChatSelector
        isOpen={isChatSelectorOpen}
        onClose={() => setIsChatSelectorOpen(false)}
        chats={getChatsForSelector()}
        onChatSelect={handleChatSelect}
        selectedChatId={currentChatId}
      />
    </>
  );
}