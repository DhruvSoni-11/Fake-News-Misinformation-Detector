import React from 'react';
import Analyzer from './components/Analyzer';
import Header from './components/Header';
import './App.css';

function App() {
  return (
    <div className="App">
      <Header />
      <main className="main-content">
        <Analyzer />
      </main>
    </div>
  );
}

export default App;