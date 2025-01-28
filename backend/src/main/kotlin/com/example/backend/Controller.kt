package com.example.backend

import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RestController

@RestController // Marks this as a REST controller
class HelloController {

    @GetMapping("/hello") // Maps GET requests to this method
    fun sayHello(): String {
        return "Hello from Spring Boot with Kotlin!"
    }
}
