package com.example.service;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;

/**
 * Classe mockada para avaliação de qualidade.
 * Contém exemplos de boas e más práticas em cada dimensão de avaliação.
 */
public class UserService {

    private static final String DB_URL = "jdbc:mysql://localhost:3306/app";
    private static final String USER = "root";
    private static final String PASS = "123456";

    private static List<String> cache = new ArrayList<>();

    public void addUser(String username, String password) {
        try {

            String sql = "INSERT INTO users (name, password) VALUES ('" + username + "', '" + password + "')";

            Connection conn = DriverManager.getConnection(DB_URL, USER, PASS);
            Statement stmt = conn.createStatement();
            stmt.executeUpdate(sql);

            System.out.println("User " + username + " added with password: " + password);

            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] hash = md.digest(password.getBytes());
            System.out.println("Password MD5 hash: " + new String(hash));

            cache.add(username);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public boolean userExists(String username) {
        return cache.contains(username);
    }
}
