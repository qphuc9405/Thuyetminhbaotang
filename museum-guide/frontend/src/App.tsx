import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { SettingsProvider } from './lib/settings'
import Home from './pages/Home'
import Chat from './pages/Chat'
import Gallery from './pages/Gallery'
import ImageDetailPage from './pages/ImageDetail'
import Timeline from './pages/Timeline'
import Stories from './pages/Stories'
import Topics from './pages/Topics'
import TopicDetailPage from './pages/TopicDetail'
import Settings from './pages/Settings'

export default function App() {
  return (
    <SettingsProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="chat" element={<Chat />} />
          <Route path="gallery" element={<Gallery />} />
          <Route path="gallery/:id" element={<ImageDetailPage />} />
          <Route path="timeline" element={<Timeline />} />
          <Route path="stories" element={<Stories />} />
          <Route path="topics" element={<Topics />} />
          <Route path="topics/:id" element={<TopicDetailPage />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Home />} />
        </Route>
      </Routes>
    </SettingsProvider>
  )
}
