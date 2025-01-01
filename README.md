# Enhanced Chat System

A modern chat application built with Next.js, featuring actor-based architecture and ML-powered message processing.

## Features

- Actor-based message processing
- Real-time ML analysis of messages
- Sentiment analysis
- Priority detection
- Message categorization
- Pattern recognition
- Self-improving ML model
- Webhook integration between chats
- Modern UI with Tailwind CSS

## Tech Stack

- Next.js
- TypeScript
- TensorFlow.js
- RxJS
- Feathers
- Socket.io
- Tailwind CSS

## Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env.local` file with required environment variables:
```env
NEXT_PUBLIC_API_URL=http://localhost:3030
```

## Development

Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Architecture

The system uses an actor-based architecture with:

### Actors
- `MessageActor`: Handles message processing and ML pipeline
- Base `Actor` class with reactive message passing

### ML Processing
- TensorFlow.js for message analysis
- Real-time sentiment analysis
- Pattern recognition
- Self-improving model through feedback

### Components
- Modern React components with TypeScript
- Tailwind CSS for styling
- Real-time updates with Socket.io
- Feathers for backend communication

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
