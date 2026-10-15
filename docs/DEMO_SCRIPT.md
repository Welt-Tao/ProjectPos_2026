# Presentation and demonstration script

Suggested duration: 7 to 9 minutes. Use the presentation slides and switch to the running application for the demonstration. Do not read the technical report on screen. Rehearse this script and adapt it to your own understanding before recording.

## 1 Introduction

Hello, my name is Taoliyuan. This is my Software Engineering Practice project, Market POS. It is an individual project covering the analysis, design and implementation of a small supermarket point-of-sale system. The two main use cases are Process Sale and Handle Returns. I will explain the project plan, the object-oriented design, and then demonstrate both workflows.

## 2 Scope and planning

The cashier records items, receives cash and issues a receipt. For returns, the cashier retrieves the original receipt and selects the quantities to refund. I have limited the scope to cash payments and goods suitable for restocking. Card processing and customer accounts are outside this version.

The plan uses a Scrum-inspired approach adapted for one person. The backlog prioritises a working sale, then returns, and finally documentation and presentation. The planned timeboxes are three days each. The implementation was produced early, so actual checkpoints are recorded separately from the ideal daily burndown. I do not treat planned dates as evidence of completed work.

## 3 Analysis and architecture

The use-case diagram identifies the cashier as the primary actor. The written use cases include both successful and unsuccessful paths. The domain model separates a sale from its sale lines, and a return from its return lines. A sale line stores the original unit price, which is necessary for a correct refund after a catalogue price changes.

The implementation has a browser presentation layer, an application layer and a domain and persistence layer. The HTTP handler delegates to POSService. Sale and SaleLine calculate amounts, while SQLiteRepository manages transactions. This separation follows the Controller and Information Expert ideas discussed in Larman's textbook.

## 4 Sale demonstration

Switch to a fresh demonstration database. Show the initial inventory: 40 milk units and 25 loaves of bread. Open Checkout. Add two milk units at two euros fifty each and one loaf at three euros twenty. The total is eight euros twenty.

Enter five euros and click Complete cash sale. The application reports insufficient cash. No sale or stock change is committed. Change the cash amount to ten euros and complete the sale. The receipt shows one euro eighty change. Milk stock is now 38 and bread stock is 24. The generated receipt ID identifies this sale for later returns.

## 5 Return demonstration

Open Returns and find the receipt. The application shows original prices and the quantities still eligible for return. Select one milk unit and enter the reason: unopened item no longer needed. Confirm the cash refund. The refund is two euros fifty, and the returned unit is restored to stock.

Now try to return two more milk units. Only one remains returnable, so the system rejects the request. This prevents the same item quantity from being refunded twice. Open Inventory to show milk stock at 39. Open Transactions to show the original sale, the return and net sales of five euros seventy.

## 6 Verification and tradeoffs

The automated test suite checks 22 scenarios, including insufficient payment, unknown products, over-selling, partial returns, original-price refunds, persistence and duplicate requests. It also tests concurrent attempts to buy or return the last eligible item. Transactions keep the receipt and stock changes consistent.

This is a local coursework application. It does not include production authentication, card integrations or a distributed database. Future work could add cashier accounts, damaged-goods handling and a receipt printer. AI assisted the implementation and document preparation. I am responsible for checking the work and explaining the design.

## 7 Closing

The project implements both required use cases with persistent records and traceable analysis and design. The repository contains the source code, tests and UML diagrams. Thank you for watching.

## Recording checklist

1. Close unrelated browser tabs and personal notifications. Keep slides and the POS browser ready.
2. Use Windows Snipping Tool screen recording if it supports audio on your machine, or your preferred screen recorder. Select the microphone and make a short test recording first.
3. Record the slides, switch to the application for the live demonstration, then return to the final slide. Ensure English narration is audible and the figures remain readable.
4. Play back the recording. Check that it includes both successful workflows, one rejected operation, UML explanation and the test result.
5. Upload the video through your own Bilibili account. Suggested title: `Software Engineering Practice - Market POS - Taoliyuan`.
6. Open the published video link in a signed-out browser to verify access. Send the final URL so the cover and submission report can be updated.
