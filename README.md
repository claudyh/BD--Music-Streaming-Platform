## Music Streaming Platform
*in Python and PostgreSQL*

&nbsp;

### 📋 Project Description
---

This project involves the development of a database-driven music streaming platform that allows users to listen to music, manage subscriptions, and interact with content. The system is designed using PostgreSQL and follows a REST API architecture to facilitate client-server communication.

&nbsp;

*Key Features*

- Three types of users: Consumers, Artists, and Administrators
- Music streaming service with premium and regular accounts
- Playlists and comments system for user interaction
- Artist and album management with record label association
- Subscription system with pre-paid cards
- REST API endpoints for all functionalities

&nbsp;

*Project Guidelines*

1. Define the database schema (ER diagram and relational model).
2. Develop an initial API to support user authentication and data retrieval.
3. Implement basic CRUD operations for users, artists, and songs.
4. Design concurrency and transaction strategies to ensure data consistency.
5. Develop the full REST API, ensuring all required endpoints are implemented.
6. Integrate database triggers for automatic playlist updates.
7. Implement user authentication (JWT-based tokens).
8. Ensure transactional integrity and concurrency control in SQL operations.
9. Test API functionality using Postman and provide test cases.

&nbsp;

*Functionalities*

**User Roles**
- Consumers: Listen to music, leave comments, and manage subscriptions.
- Premium Users: Create private/public playlists and access exclusive content.
- Artists: Upload songs and albums, associate with labels, and track statistics.
- Administrators: Manage artists, generate pre-paid cards, and oversee platform activity.

**Rest API**
- User Registration & Authentication: Create accounts, login, and manage session tokens.
- Music Management: Add and retrieve songs, albums, and artist details.
- Playlist Management: Create, edit, and manage playlists (premium users only).
- Subscription System: Upgrade accounts via pre-paid cards with fixed values (10, 25, 50€).
- Commenting System: Users can leave feedback and reply to comments.
- Reporting & Analytics: Generate monthly reports on song play statistics.

&nbsp;

*Setup*

**Database:** PostgreSQL with schema and data initialization scripts.
**API:** REST-based, tested using Postman collections.

&nbsp;

---

**NOTE:** The project development has been completed, with all main actions functioning. Instead of a regular/premium column, we checked subscription status when needed. We also added an endpoint to show a consumer’s top 10 playlists, sorted by play count. However, the project still requires further improvements and is missing rollbacks, which are crucial for database security. This project was developed within the scope of a Computer Science course by Cláudia Torres, Daniel Veiga and Maria João Rosa.
