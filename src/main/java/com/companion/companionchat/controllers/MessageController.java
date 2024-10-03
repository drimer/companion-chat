package com.companion.companionchat.controllers;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
public class MessageController {

    private record NewMessageDto(
        String conversationId,
        String message
    ) { }

    ;

    @PostMapping("/messages")
    public String sendNewMessageInConversation(@RequestBody NewMessageDto newMessageDto) {
        return "Sent message " + newMessageDto.message;
    }

    @GetMapping("/conversations/{id}/messages")
    public List<String> getMessagesInConversation(@PathVariable String id) {
        return List.of("Message 1", "Message 2");
    }

}
