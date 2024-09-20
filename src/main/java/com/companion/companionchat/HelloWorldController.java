package com.companion.companionchat;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloWorldController {

    @GetMapping("/hello-world")
    public String getEndpoint() {
        return "Hola Mundo";
    }

}
