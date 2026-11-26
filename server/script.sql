create database oh_my_agent;
use oh_my_agent;

SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- 1. 用户表
CREATE TABLE `user` (
  `id` char(36) NOT NULL,
  `username` varchar(64) NOT NULL,
  `nickname` varchar(64) NOT NULL DEFAULT '',
  `password` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. 用户模型配置表
CREATE TABLE `model_config` (
  `id` char(36) NOT NULL,
  `user_id` char(36) NOT NULL,
  `display_name` varchar(128) NOT NULL,
  `provider` varchar(32) NOT NULL DEFAULT 'custom',
  `model_name` varchar(128) NOT NULL,
  `base_url` varchar(512) NOT NULL,
  `context_window` int NOT NULL DEFAULT 128000,
  `max_output_tokens` int NOT NULL DEFAULT 4096,
  `api_key_ciphertext` varchar(512) NOT NULL,
  `api_key_nonce` varchar(64) NOT NULL,
  `api_key_salt` varchar(64) NOT NULL,
  `is_default` tinyint NOT NULL DEFAULT 0,
  `is_active` tinyint NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_model_config_user_deleted` (`user_id`, `deleted_at`),
  CONSTRAINT `fk_model_config_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 系统提示词
CREATE TABLE `system_prompts` (
  `id` int NOT NULL,
  `user_id` char(36) NULL DEFAULT NULL,
  `name` varchar(256) NOT NULL,
  `prompt` text NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_system_prompts_user_id` (`user_id`),
  CONSTRAINT `fk_system_prompts_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. 会话
CREATE TABLE `session` (
  `id` char(36) NOT NULL,
  `title` varchar(128) NOT NULL DEFAULT '',
  `user_id` char(36) NOT NULL,
  `model_config_id` char(36) NULL DEFAULT NULL,
  `system_prompt` int NULL DEFAULT 0,
  `input_token_used` bigint NOT NULL DEFAULT 0,
  `output_token_used` bigint NOT NULL DEFAULT 0,
  `is_pinned` tinyint NOT NULL DEFAULT 0,
  `sort_order` int NOT NULL DEFAULT 0,
  `last_conversation_at` datetime NULL DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_session_user_deleted_last` (`user_id`, `deleted_at`, `last_conversation_at`),
  KEY `idx_session_user_pinned_sort` (`user_id`, `is_pinned`, `sort_order`),
  KEY `idx_session_model_config_id` (`model_config_id`),
  KEY `idx_session_system_prompt` (`system_prompt`),
  CONSTRAINT `fk_session_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_session_model_config`
    FOREIGN KEY (`model_config_id`) REFERENCES `model_config` (`id`)
    ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_session_system_prompt`
    FOREIGN KEY (`system_prompt`) REFERENCES `system_prompts` (`id`)
    ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. 对话消息表
CREATE TABLE `chat_message` (
  `id` char(36) NOT NULL,
  `session_id` char(36) NOT NULL,
  `parent_id` char(36) NULL DEFAULT NULL,
  `seq` bigint NOT NULL,
  `model_config_id` char(36) NULL DEFAULT NULL,
  `model_name` varchar(128) NULL DEFAULT NULL,
  `role` varchar(16) NOT NULL,
  `content` mediumtext NULL,
  `reasoning_content` mediumtext NULL,
  `input_token` int NOT NULL DEFAULT 0,
  `output_token` int NOT NULL DEFAULT 0,
  `msg_status` tinyint NOT NULL DEFAULT 0,
  `error_message` varchar(512) NULL DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_chat_message_session_seq` (`session_id`, `seq`),
  KEY `idx_chat_message_parent_id` (`parent_id`),
  KEY `idx_chat_message_model_config_id` (`model_config_id`),
  CONSTRAINT `fk_chat_message_session`
    FOREIGN KEY (`session_id`) REFERENCES `session` (`id`)
    ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_chat_message_model_config`
    FOREIGN KEY (`model_config_id`) REFERENCES `model_config` (`id`)
    ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_chat_message_parent`
    FOREIGN KEY (`parent_id`) REFERENCES `chat_message` (`id`)
    ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 初始化默认提示词：必须在写入 session 之前执行。
-- session.system_prompt 默认值为 0，依赖 system_prompts.id = 0 存在。
INSERT INTO `system_prompts`
  (`id`, `user_id`, `name`, `prompt`, `created_at`, `updated_at`, `deleted_at`)
VALUES
  (0, NULL, '默认提示词', 'You are a helpful assistant.', UTC_TIMESTAMP(), UTC_TIMESTAMP(), NULL)
ON DUPLICATE KEY UPDATE
  `name` = VALUES(`name`),
  `prompt` = VALUES(`prompt`),
  `updated_at` = UTC_TIMESTAMP();