package com.companion.companionchat.controllers;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ConversationController {

    @PostMapping("/conversations")
    public String startNewConversation(String persona) {
        return "Conversation Id: 1";
    }

    @GetMapping("/conversations/{conversationId}")
    public String getConversation(
        @PathVariable String conversationId
    ) {
        return "Conversation Id: " + conversationId;
    }

}
