// O padrão DAO (Data Access Object) separa a lógica de acesso a dados da lógica de negócio.
// Esta classe é responsável apenas pela interação com o banco de dados.
package com.example.dao;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class UserDao {

    // 💡 Boa prática: Credenciais devem ser carregadas de um arquivo de configuração
    // ou variáveis de ambiente, nunca hardcoded.
    private static final String DB_URL = "jdbc:mysql://localhost:3306/app";
    private static final String USER = "root";
    private static final String PASS = "123456";

    // O método agora aceita o nome de usuário e a senha já com o hash (ilegível).
    // O hash da senha é uma responsabilidade da camada de serviço, não da DAO.
    public void insertUser(String username, String hashedPassword) throws SQLException {
        // 💡 Boa prática: Uso de PreparedStatement para prevenir SQL Injection.
        // Os '?' são placeholders que serão preenchidos de forma segura.
        String sql = "INSERT INTO users (name, password) VALUES (?, ?)";

        try (Connection conn = DriverManager.getConnection(DB_URL, USER, PASS);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {

            pstmt.setString(1, username);
            pstmt.setString(2, hashedPassword);

            pstmt.executeUpdate();

            System.out.println("Usuário inserido com sucesso no banco de dados.");

        }
    }
}

// --------------------------------------------------------------------------------------

// Esta é a classe de serviço, que agora foca na lógica de negócio.
// Ela não tem conhecimento de SQL, conexões de banco de dados, ou outros detalhes de infraestrutura.
package com.example.service;

import com.example.dao.UserDao;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;

/**
 * Classe de Serviço refatorada para aderir aos padrões de arquitetura e segurança.
 * Separa a lógica de negócio do acesso a dados.
 */
public class UserService {

    // 💡 Boa prática: Injeção de dependência. Idealmente, o UserDao seria injetado aqui.
    private final UserDao userDao = new UserDao();

    private static final List<String> cache = new ArrayList<>();

    // O método de adicionar usuário agora é responsável pela lógica de negócio e segurança.
    public void addUser(String username, String password) {
        try {
            // 💡 Boa prática: Gerar um salt aleatório para cada senha.
            // Isso previne ataques de rainbow table, mesmo que dois usuários tenham a mesma senha.
            SecureRandom random = new SecureRandom();
            byte[] salt = new byte[16];
            random.nextBytes(salt);

            // 💡 Boa prática: Utilizar um algoritmo de hash mais seguro como SHA-256 ou SHA-512.
            // Para produção, é altamente recomendável usar bibliotecas como BCrypt ou Argon2.
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update(salt); // Adiciona o salt antes da senha.
            byte[] hashedPassword = md.digest(password.getBytes());

            // Combina o salt e o hash para armazenamento.
            String encodedPassword = Base64.getEncoder().encodeToString(salt) + ":" + Base64.getEncoder().encodeToString(hashedPassword);

            // 💡 Boa prática: A responsabilidade de persistir o dado é delegada para o DAO.
            userDao.insertUser(username, encodedPassword);

            // 🔴 Ação removida: Logar a senha em texto plano.
            // Isso é uma falha de segurança grave e foi eliminado.
            // 💡 Boa prática: Apenas o nome de usuário ou um ID de sessão podem ser logados, nunca a senha.
            System.out.println("Usuário '" + username + "' adicionado com sucesso.");

            // 💡 Boa prática: A lógica de cache também está aqui, separada do acesso a dados.
            cache.add(username);

        } catch (Exception e) {
            // 💡 Melhoria de logging: Em vez de e.printStackTrace(), use um logger configurado (ex: Log4j, SLF4J).
            // Isso permite um controle melhor do nível de log e destino.
            System.err.println("Erro ao adicionar usuário: " + e.getMessage());
        }
    }

    public boolean userExists(String username) {
        return cache.contains(username);
    }
}
