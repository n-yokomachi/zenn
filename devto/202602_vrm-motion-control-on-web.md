---
title: "Controlling VRM Character Motions for an AI Agent on the Web"
emoji: "🚶🏻"
type: "tech"
topics: [vrm, threejs, nextjs, typescript, aituber]
published: false
---

> This article is an AI-assisted translation of a Japanese technical article.

## Introduction
I'm currently working on a personal AI agent project and decided to use a 3D model as the user interface.
Since I didn't have the knowledge to build everything from scratch, I leveraged [AITuberKit](https://github.com/tegnike/aituber-kit), an OSS project I'd been aware of for a while, to quickly set up the frontend.

![](https://storage.googleapis.com/zenn-user-upload/481cdad6c3c1-20260221.png)

By the way, I also covered this topic in a recent lightning talk.
Here are the slides:
{% speakerdeck 345f449950cf468d8fd52422979c3026 %}


## Tech Stack

- VRM model creation: [VRoid Studio](https://vroid.com/studio)
- Web frontend: Next.js, TypeScript
- VRM rendering & control: [three-vrm](https://github.com/pixiv/three-vrm) (v3.0.0), Three.js
- Base kit: [AITuberKit](https://github.com/tegnike/aituber-kit)
- Agent implementation: Strands Agents, Amazon Bedrock AgentCore *Not covered in detail in this article*

# VRM and VRoid Studio
VRM is a file format designed for 3D avatars.
With [VRoid Studio](https://vroid.com/studio), you can create characters and export them in VRM format without any 3D modeling knowledge.
In my case, my only prior experience was creating characters in video games, but I was able to create two models (male and female) in about an hour — that's how easy it is.

https://x.com/_cityside/status/2019742015617994773

# What AITuberKit Can Do
[AITuberKit](https://github.com/tegnike/aituber-kit) is an OSS that displays VRM models in a web browser and bundles features like LLM-powered chat, facial expression control, and speech synthesis.

Here are some of the key features AITuberKit provides:

- VRM model display, facial expression control, and lip-sync
- LLM-powered chatbot functionality
- Speech synthesis API integration
- YouTube streaming integration
- Multimodal input
- etc.

For my project, since I'm building it as a personal AI agent, I'm using AITuberKit's base features like VRM display control and chatbot functionality while adding heavy customizations on top.

# Implementing Motion Control

Here's where we get to the main topic.
AITuberKit supports switching facial expressions (smile, angry face, etc.) out of the box, so I decided to implement additional body motions (bowing, extending a hand, etc.).

https://x.com/_cityside/status/2016874430056845502

## Architecture Overview

Here's the overall picture of the motion control system:

```
LLM Response
  ↓ Streaming parser
  ├─ [emotion] Emotion tag → ExpressionController → Facial expression control
  └─ [bow/present] Motion tag → GestureController → Bone control
                                         ↑
                                    EmoteController (conflict resolution)
```

The `EmoteController` sits between facial expressions and motions to handle conflicts between them.

## Motion Definitions

Motions are implemented by defining bone rotations as keyframes.

Here's an example definition for a bow:

```typescript
// src/features/emoteController/gestureController.ts
interface BoneRotation {
  bone: VRMHumanBoneName
  rotation: THREE.Quaternion
}

interface GestureKeyframe {
  duration: number
  bones: BoneRotation[]
}

interface GestureDefinition {
  keyframes: GestureKeyframe[]
  holdDuration: number
  closeEyes?: boolean
}
```

For the bow motion, three bones — spine, chest, and neck — are each rotated forward to create a more natural-looking bow rather than simply bending at the waist.
The arm bones are also adjusted to achieve a natural posture.

```typescript
// src/features/emoteController/gestureController.ts
this._gestures.set('bow', {
  keyframes: [
    {
      duration: 1.0,
      bones: [
        {
          bone: 'spine',
          rotation: new THREE.Quaternion().setFromEuler(
            new THREE.Euler(0.25, 0, 0)
          ),
        },
        {
          bone: 'chest',
          rotation: new THREE.Quaternion().setFromEuler(
            new THREE.Euler(0.15, 0, 0)
          ),
        },
        {
          bone: 'neck',
          rotation: new THREE.Quaternion().setFromEuler(
            new THREE.Euler(0.12, 0, 0)
          ),
        },
        // Arm bones are also adjusted (omitted)
      ],
    },
  ],
  holdDuration: 1.0,
  closeEyes: true, // Close eyes during the bow
})
```


# Triggering Motions from LLM Responses


The character's expressions are controlled by having the LLM output emotion and motion tags in its responses.

Emotion tags are implemented by default in AITuberKit. The LLM response looks like this:
```
[happy]Thank you so much!
```

Motion tags are a custom addition. They appear in the response just like emotion tags:
```
Welcome! [bow]What kind of fragrance are you looking for today?
```

When both emotion and motion tags appear simultaneously, both are triggered.
For example, `[happy][bow]` results in the character bowing with a smile.


The system prompt includes the following instructions:

```typescript
`
## Emotional Expression
The format for conversation text is as follows. Choose the single most appropriate emotion for the entire response and prepend the emotion tag at the beginning.
[{neutral|happy|angry|sad|relaxed|surprised}]{conversation text}
`
```


# Handling Conflicts Between Expressions and Motions

Simply applying both facial expressions and motions at the same time can cause unexpected behavior, so I've added the following controls.
For example, having the eyes open during a bow looked unnatural, so I set `closeEyes: true` to close the eyes on the motion control side.

The `EmoteController` manages this by passing flags between controllers:

```typescript
// src/features/emoteController/emoteController.ts
public updateExpression(delta: number) {
  const isEmotionActive = this._expressionController.isEmotionActive
  // Skip auto-blink if the motion is closing eyes and expression is neutral
  const skipAutoBlink =
    this._gestureController.isClosingEyes && !isEmotionActive
  this._expressionController.update(delta, skipAutoBlink)
}

public updateGesture(delta: number) {
  const isEmotionActive = this._expressionController.isEmotionActive
  // Skip motion eye-close if an emotion expression is active
  this._gestureController.update(delta, isEmotionActive)
}
```

The emotion expressions and the motion's eye-close feature are mutually exclusive.
When the emotion is `neutral`, the motion side closes the eyes. When an emotion is active, the motion's eye-close is disabled and control is handed to the expression side.


# Wrapping Up

Using a chat UI as the frontend for an AI agent is a very common approach, but even a simple model like this feels lively just by having it move around, which makes it really fun.
That said, controlling motions can be quite tricky — figuring out which bones to rotate and by how much is surprisingly difficult.
For more complex motions, you could look into purchasing motion packs, which might be a good option.
