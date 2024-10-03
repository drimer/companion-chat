package com.companion.companionchat.controllers;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class PersonasController {

    @GetMapping("/personas")
    public List<String> getPersonas() {
        return List.of("Persona 1", "Persona 2");
    }

}
