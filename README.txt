
Introduction to Internet course project


Program contacts university server via TCP, and receives go-ahead to contact via UDP. Receives a list of words, reverses it and returns it to server.

Additional features are encryption and multipart messaging.

When contacting server via TCP, also receives encryption key. De-encrypts received message using key, and encrypts reversed word list before sending it.
Due to multipart messaging, word list is received in multiple packets, that must be joined before reversing, and split again before returning them.


Andrea Peltokorpi, 2018