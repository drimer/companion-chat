package com.companion.companionchat;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloWorldController {

    @GetMapping
    public String getEndpoint() {
        return "Hola Mundo";
    }

}
